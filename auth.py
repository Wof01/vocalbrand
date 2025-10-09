"""Lightweight auth & user management (SQLite) for VocalBrand.
Not production hardened (no rate limiting / email verification)."""
from __future__ import annotations
import sqlite3
import os
from typing import Optional, Tuple

# Hashing strategy selection
HASH_SCHEME = os.getenv("AUTH_HASH_SCHEME", "pbkdf2").lower()  # values: bcrypt | bcrypt_sha256 | pbkdf2
PASSWORD_MAX_LEN = 256  # hard limit to avoid abuse

try:
    if HASH_SCHEME in {"bcrypt", "bcrypt_sha256"}:
        from passlib.hash import bcrypt  # type: ignore
        from passlib.hash import pbkdf2_sha256  # type: ignore
    else:
        from passlib.hash import pbkdf2_sha256  # type: ignore
except ImportError as e:  # pragma: no cover
    raise SystemExit("Missing passlib. Install with: pip install 'passlib[bcrypt]'" ) from e

import secrets

DB_URL = os.getenv("DATABASE_URL", "sqlite:///vocalbrand.db")
if DB_URL.startswith("sqlite:///"):
    DB_PATH = DB_URL.replace("sqlite:///", "")
else:
    DB_PATH = "vocalbrand.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    subscription_active INTEGER DEFAULT 0,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    free_generations_used INTEGER DEFAULT 0,
    minutes_balance INTEGER DEFAULT 0,
    setup_credits INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    conn = _get_conn()
    with conn:
        conn.executescript(SCHEMA)
        # Migrate existing tables to add new columns if missing
        try:
            conn.execute("SELECT free_generations_used FROM users LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE users ADD COLUMN free_generations_used INTEGER DEFAULT 0")
        
        try:
            conn.execute("SELECT minutes_balance FROM users LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE users ADD COLUMN minutes_balance INTEGER DEFAULT 0")
        
        try:
            conn.execute("SELECT setup_credits FROM users LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE users ADD COLUMN setup_credits INTEGER DEFAULT 0")
    conn.close()


def _truncate_for_bcrypt(pw: str) -> str:
    """Legacy truncation helper.

    NOTE: bcrypt only uses first 72 bytes of the *byte sequence* (after utf-8
    encoding). Historically we truncated the *string* which can still exceed
    72 bytes when it contains multi‑byte characters (emoji, accents). We keep
    this for backward compatibility with previously stored hashes.
    """
    return pw[:72]


def _sha256_hex(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def _normalize_secret(password: str, pepper: str) -> tuple[str, bool]:
    """Return a safe secret string for bcrypt.

    NEW STRATEGY (ALWAYS for bcrypt variants): always SHA-256 the combined
    password+pepper (after length cap) -> hex digest (64 ASCII chars).
    This mimics passlib's bcrypt_sha256 scheme and removes the 72-byte limit.

    We return (secret, True) as flag meaning pre-hash applied, to help with
    fallback logic in verification for legacy hashes.
    """
    pw = (password or "")[:PASSWORD_MAX_LEN]
    combined = (pw + pepper).encode("utf-8")
    return _sha256_hex(combined), True


_BCRYPT_USABLE: bool | None = None

def _probe_bcrypt() -> bool:
    """Return True if bcrypt backend appears functional.

    We attempt a tiny hash+verify cycle. If any exception occurs we mark
    unusable for the process lifetime so we immediately fall back to pbkdf2.
    """
    global _BCRYPT_USABLE
    if _BCRYPT_USABLE is not None:
        return _BCRYPT_USABLE
    if HASH_SCHEME not in {"bcrypt", "bcrypt_sha256"}:
        _BCRYPT_USABLE = False
        return False
    try:  # pragma: no cover (env specific)
        test_secret = "probe_secret"
        h = bcrypt.hash(test_secret)
        _BCRYPT_USABLE = bcrypt.verify(test_secret, h)
    except Exception as exc:  # noqa: BLE001
        print(f"[vocalbrand.auth] WARN bcrypt probe failed – falling back to pbkdf2 ({exc})")
        _BCRYPT_USABLE = False
    return bool(_BCRYPT_USABLE)


def hash_backend_status() -> dict:
    """Expose current hashing backend status for UI or diagnostics.

    Returns dict like: {"requested": HASH_SCHEME, "using": "bcrypt"|"pbkdf2", "bcrypt_usable": bool}
    """
    usable = _probe_bcrypt()
    using = "bcrypt" if (HASH_SCHEME in {"bcrypt", "bcrypt_sha256"} and usable) else "pbkdf2"
    return {"requested": HASH_SCHEME, "using": using, "bcrypt_usable": usable}


def hash_password(password: str, pepper: str = "") -> str:
    """Hash a password with optional pepper.

    Strategy:
      * If bcrypt selected & backend works: pre-hash with sha256 (bcrypt_sha256 style)
      * If bcrypt unusable (or raises runtime errors): fall back to pbkdf2 transparently
      * Always cap password length to PASSWORD_MAX_LEN
    """
    pw = (password or "")[:PASSWORD_MAX_LEN]
    if HASH_SCHEME in {"bcrypt", "bcrypt_sha256"} and _probe_bcrypt():
        secret, _ = _normalize_secret(pw, pepper)
        try:
            return bcrypt.hash(secret)
        except Exception as exc:  # noqa: BLE001
            print(f"[vocalbrand.auth] WARN bcrypt hashing failed at runtime – fallback to pbkdf2 ({exc})")
    return pbkdf2_sha256.hash(pw + pepper)


def verify_password(password: str, hashed: str, pepper: str = "") -> bool:
    """Verify password with pepper; supports legacy truncated bcrypt hashes.

    Order for bcrypt:
      1. Try modern pre-hash (sha256 of password+pepper)
      2. Try legacy truncated & raw forms for backward compatibility
      3. Fallback to pbkdf2 verification if hash is pbkdf2 or bcrypt fails
    """
    try:
        pw = (password or "")[:PASSWORD_MAX_LEN]
        combined = pw + pepper

        # Direct pbkdf2 hash (regardless of configured scheme)
        if hashed.startswith("$pbkdf2-sha256$"):
            return pbkdf2_sha256.verify(combined, hashed)

        # Bcrypt path if selected & usable
        if HASH_SCHEME in {"bcrypt", "bcrypt_sha256"} and _probe_bcrypt():
            raw_bytes = combined.encode("utf-8")
            candidates = [
                _sha256_hex(raw_bytes),             # modern pre-hash
                _truncate_for_bcrypt(combined),     # legacy truncated
                combined,                           # legacy raw
            ]
            for cand in candidates:
                try:
                    if bcrypt.verify(cand, hashed):
                        return True
                except Exception:
                    continue
            # Rescue attempt: maybe stored hash actually pbkdf2
            try:
                return pbkdf2_sha256.verify(combined, hashed)
            except Exception:
                return False

        # Default pbkdf2 verification path
        return pbkdf2_sha256.verify(combined, hashed)
    except Exception:
        return False


def register_user(email: str, password: str, pepper: str = "") -> Tuple[bool, str]:
    conn = _get_conn()
    try:
        with conn:
            conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email.lower().strip(), hash_password(password, pepper)),
            )
        return True, "registered"
    except sqlite3.IntegrityError:
        return False, "email_exists"
    finally:
        conn.close()


def authenticate(email: str, password: str, pepper: str = "") -> Tuple[bool, Optional[int]]:
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT id, password_hash FROM users WHERE email=?", (email.lower().strip(),))
        row = cur.fetchone()
        if not row:
            return False, None
        uid, hashv = row
        if verify_password(password, hashv, pepper):
            return True, uid
        return False, None
    finally:
        conn.close()


def get_user(uid: int):
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT id, email, subscription_active FROM users WHERE id=?", (uid,))
        row = cur.fetchone()
        if row:
            return {"id": row[0], "email": row[1], "subscription_active": bool(row[2])}
    finally:
        conn.close()
    return None


def set_subscription(uid: int, active: bool, stripe_sub_id: str | None = None):
    conn = _get_conn()
    with conn:
        conn.execute(
            "UPDATE users SET subscription_active=?, stripe_subscription_id=? WHERE id=?",
            (1 if active else 0, stripe_sub_id, uid),
        )
    conn.close()


def get_free_usage(uid: int) -> int:
    """Return the number of free generations used by this user."""
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT free_generations_used FROM users WHERE id=?", (uid,))
        row = cur.fetchone()
        if row:
            return row[0] or 0
        return 0
    finally:
        conn.close()


def increment_free_usage(uid: int) -> int:
    """Increment the free generation counter and return the new count."""
    conn = _get_conn()
    try:
        with conn:
            conn.execute(
                "UPDATE users SET free_generations_used = free_generations_used + 1 WHERE id=?",
                (uid,),
            )
        cur = conn.execute("SELECT free_generations_used FROM users WHERE id=?", (uid,))
        row = cur.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def add_minutes_balance(uid: int, minutes: int) -> int:
    """Add minutes to user's balance and return the new total."""
    conn = _get_conn()
    try:
        with conn:
            conn.execute(
                "UPDATE users SET minutes_balance = minutes_balance + ? WHERE id=?",
                (minutes, uid),
            )
        cur = conn.execute("SELECT minutes_balance FROM users WHERE id=?", (uid,))
        row = cur.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def get_minutes_balance(uid: int) -> int:
    """Get user's current minutes balance."""
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT minutes_balance FROM users WHERE id=?", (uid,))
        row = cur.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def add_setup_credits(uid: int, credits: int) -> int:
    """Add setup service credits to user's account and return the new total."""
    conn = _get_conn()
    try:
        with conn:
            conn.execute(
                "UPDATE users SET setup_credits = setup_credits + ? WHERE id=?",
                (credits, uid),
            )
        cur = conn.execute("SELECT setup_credits FROM users WHERE id=?", (uid,))
        row = cur.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def get_setup_credits(uid: int) -> int:
    """Get user's setup service credits."""
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT setup_credits FROM users WHERE id=?", (uid,))
        row = cur.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def get_user_by_email(email: str):
    """Get user by email address."""
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT id, email, subscription_active, minutes_balance, setup_credits FROM users WHERE email=?",
            (email.lower().strip(),),
        )
        row = cur.fetchone()
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "subscription_active": bool(row[2]),
                "minutes_balance": row[3] or 0,
                "setup_credits": row[4] or 0,
            }
    finally:
        conn.close()
    return None


def ensure_demo_user():
    # For quick demos create a demo user if none exist
    conn = _get_conn()
    cur = conn.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    if count == 0:
        register_user("demo@vocalbrand.local", "demo123")
    conn.close()

if __name__ == "__main__":
    init_db()
    ensure_demo_user()
    print(f"DB initialized using hash scheme: {HASH_SCHEME}")
