"""Lightweight auth & user management for VocalBrand.
Supports both SQLite (local) and PostgreSQL (production).
Not production hardened (no rate limiting / email verification)."""
from __future__ import annotations
import os
from typing import Optional, Tuple

# Import database adapter
from db_adapter import db_adapter, get_db_type, get_db_info

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


def init_db():
    """Initialize database schema with support for both SQLite and PostgreSQL."""
    print(f"[VocalBrand] Initializing database: {get_db_type()}")
    
    # Create schema
    schema = db_adapter.get_schema_sql()
    
    with db_adapter.get_connection() as conn:
        cursor = conn.cursor()
        # Execute schema (split by semicolon for multi-statement)
        for statement in schema.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        conn.commit()
        cursor.close()
    
    # Migrate existing tables to add new columns if missing
    db_adapter.add_column("users", "free_generations_used", "INTEGER", 0)
    db_adapter.add_column("users", "minutes_balance", "INTEGER", 0)
    db_adapter.add_column("users", "setup_credits", "INTEGER", 0)
    
    print(f"[VocalBrand] Database initialized successfully: {get_db_type()}")


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
    """Register a new user."""
    try:
        result = db_adapter.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email.lower().strip(), hash_password(password, pepper))
        )
        return True, "registered"
    except Exception as e:
        # Check if it's a duplicate email error
        error_str = str(e).lower()
        if "unique" in error_str or "duplicate" in error_str:
            return False, "email_exists"
        raise


def authenticate(email: str, password: str, pepper: str = "") -> Tuple[bool, Optional[int]]:
    """Authenticate a user and return (success, user_id)."""
    row = db_adapter.execute(
        "SELECT id, password_hash FROM users WHERE email=?",
        (email.lower().strip(),),
        fetch='one'
    )
    
    if not row:
        return False, None
    
    uid, hashv = row[0], row[1]
    if verify_password(password, hashv, pepper):
        return True, uid
    return False, None


def get_user(uid: int):
    """Get user information by user ID."""
    row = db_adapter.execute(
        "SELECT id, email, subscription_active FROM users WHERE id=?",
        (uid,),
        fetch='one'
    )
    
    if row:
        return {"id": row[0], "email": row[1], "subscription_active": bool(row[2])}
    return None


def set_subscription(uid: int, active: bool, stripe_sub_id: str | None = None):
    """Set user's subscription status."""
    db_adapter.execute(
        "UPDATE users SET subscription_active=?, stripe_subscription_id=? WHERE id=?",
        (1 if active else 0, stripe_sub_id, uid)
    )


def get_free_usage(uid: int) -> int:
    """Return the number of free generations used by this user."""
    row = db_adapter.execute(
        "SELECT free_generations_used FROM users WHERE id=?",
        (uid,),
        fetch='one'
    )
    return row[0] if row else 0


def increment_free_usage(uid: int) -> int:
    """Increment the free generation counter and return the new count."""
    db_adapter.execute(
        "UPDATE users SET free_generations_used = free_generations_used + 1 WHERE id=?",
        (uid,)
    )
    
    row = db_adapter.execute(
        "SELECT free_generations_used FROM users WHERE id=?",
        (uid,),
        fetch='one'
    )
    return row[0] if row else 0


def add_minutes_balance(uid: int, minutes: int) -> int:
    """Add minutes to user's balance and return the new total."""
    db_adapter.execute(
        "UPDATE users SET minutes_balance = minutes_balance + ? WHERE id=?",
        (minutes, uid)
    )
    
    row = db_adapter.execute(
        "SELECT minutes_balance FROM users WHERE id=?",
        (uid,),
        fetch='one'
    )
    return row[0] if row else 0


def get_minutes_balance(uid: int) -> int:
    """Get user's current minutes balance."""
    row = db_adapter.execute(
        "SELECT minutes_balance FROM users WHERE id=?",
        (uid,),
        fetch='one'
    )
    return row[0] if row else 0


def add_setup_credits(uid: int, credits: int) -> int:
    """Add setup service credits to user's account and return the new total."""
    db_adapter.execute(
        "UPDATE users SET setup_credits = setup_credits + ? WHERE id=?",
        (credits, uid)
    )
    
    row = db_adapter.execute(
        "SELECT setup_credits FROM users WHERE id=?",
        (uid,),
        fetch='one'
    )
    return row[0] if row else 0


def get_setup_credits(uid: int) -> int:
    """Get user's setup service credits."""
    row = db_adapter.execute(
        "SELECT setup_credits FROM users WHERE id=?",
        (uid,),
        fetch='one'
    )
    return row[0] if row else 0


def get_user_by_email(email: str):
    """Get user by email address."""
    row = db_adapter.execute(
        "SELECT id, email, subscription_active, minutes_balance, setup_credits FROM users WHERE email=?",
        (email.lower().strip(),),
        fetch='one'
    )
    
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "subscription_active": bool(row[2]),
            "minutes_balance": row[3] or 0,
            "setup_credits": row[4] or 0,
        }
    return None


def ensure_demo_user():
    """Create a demo user if no users exist."""
    row = db_adapter.execute("SELECT COUNT(*) FROM users", fetch='one')
    count = row[0] if row else 0
    
    if count == 0:
        register_user("demo@vocalbrand.local", "demo123")


# -------------------------
# Stripe session idempotency
# -------------------------

def has_processed_session(session_id: str) -> bool:
    """Return True if this Stripe checkout session was already processed."""
    if not session_id:
        return False
    
    row = db_adapter.execute(
        "SELECT 1 FROM processed_sessions WHERE session_id=?",
        (session_id,),
        fetch='one'
    )
    return row is not None


def mark_processed_session(
    user_id: int | None,
    session_id: str,
    kind: str,
    amount_cents: int | None = None,
    currency: str | None = None,
    details: str | None = None,
) -> bool:
    """Persist a processed Stripe session (safe to call multiple times).

    Returns True if inserted, False if it already existed or on failure.
    """
    if not session_id:
        return False
    
    try:
        # Try to insert
        db_adapter.execute(
            "INSERT INTO processed_sessions (session_id, user_id, kind, amount_cents, currency, details) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, user_id, kind, amount_cents, currency, details)
        )
        return True
    except Exception:
        # Already exists or other error
        return has_processed_session(session_id)

if __name__ == "__main__":
    init_db()
    ensure_demo_user()
    print(f"DB initialized using hash scheme: {HASH_SCHEME}")
