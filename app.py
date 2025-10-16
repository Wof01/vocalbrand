"""Main Streamlit application for VocalBrand Supreme."""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import queue
import shutil
import sys
import threading
import time
import subprocess
import platform
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
from dotenv import load_dotenv

# Optional native recorder components (preferred path).
# - PyPI: streamlit-audiorecorder → from audiorecorder import audiorecorder
# - GitHub/pip: streamlit_audio_recorder → from streamlit_audio_recorder import st_audiorec
# Try both to maximize compatibility across environments.
try:
    from audiorecorder import audiorecorder  # type: ignore
except Exception:  # pragma: no cover
    try:
        from streamlit_audiorecorder import audiorecorder  # type: ignore
    except Exception:  # pragma: no cover
        audiorecorder = None

try:
    from streamlit_audio_recorder import st_audiorec  # type: ignore
except Exception:  # pragma: no cover
    st_audiorec = None

# Third fallback: streamlit_mic_recorder (actively maintained)
try:
    from streamlit_mic_recorder import mic_recorder  # type: ignore
except Exception:  # pragma: no cover
    mic_recorder = None

# Runtime self-heal for missing recorder components on Streamlit Cloud/Linux.
def _try_import_recorders() -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
    _aud = None
    _st = None
    _mic = None
    try:
        from audiorecorder import audiorecorder as _ar  # type: ignore
        _aud = _ar
    except Exception:
        try:
            from streamlit_audiorecorder import audiorecorder as _ar  # type: ignore
            _aud = _ar
        except Exception:
            _aud = None
    try:
        from streamlit_audio_recorder import st_audiorec as _sa  # type: ignore
        _st = _sa
    except Exception:
        _st = None
    try:
        from streamlit_mic_recorder import mic_recorder as _mr  # type: ignore
        _mic = _mr
    except Exception:
        _mic = None
    return _aud, _st, _mic


def _pip_install_if_missing(pkgs: List[str], timeout: int = 240) -> bool:
    """Attempt to install packages via pip at runtime. Safe on Streamlit Cloud.

    Returns True if pip exited with code 0, False otherwise.
    """
    try:
        cmd = [sys.executable, "-m", "pip", "install", "-q"] + pkgs
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0
    except Exception:
        return False


def ensure_native_recorder_available() -> None:
    """If recorder components are missing, try to auto-install on Linux/Cloud.

    This keeps the app "locked" functionally while self-healing the environment.
    No-op on Windows/local where the user already has everything.
    """
    global audiorecorder, st_audiorec, mic_recorder
    if (audiorecorder is not None) or (st_audiorec is not None) or (mic_recorder is not None):
        return
    # Heuristic: Streamlit Cloud is Linux. Avoid doing this on Windows.
    if platform.system().lower() != "linux":
        return
    # Allow disabling via env if ever needed.
    if os.getenv("AUTO_INSTALL_RECORDER", "1") != "1":
        return
    # Try installing both common recorder components, then reimport.
    pkgs = [
        "streamlit-audiorecorder>=0.0.2",
        "git+https://github.com/stefanrmmr/streamlit_audio_recorder.git@777d18114130137d492c0378a86631fff1ff1be5#egg=streamlit-audiorec",
        "streamlit-mic-recorder>=0.0.8",
    ]
    success = _pip_install_if_missing(pkgs)
    # Re-attempt imports regardless; success flag is just advisory.
    _aud, _st, _mic = _try_import_recorders()
    if _aud is not None:
        audiorecorder = _aud
    if _st is not None:
        st_audiorec = _st
    if _mic is not None:
        mic_recorder = _mic

AUTH_IMPORT_ERROR: Optional[Exception] = None
try:
    from auth import (
        authenticate,
        ensure_demo_user,
        get_user,
        get_free_usage,
        increment_free_usage,
        get_minutes_balance,
        get_setup_credits,
        get_user_by_email,
        hash_backend_status,
        init_db,
        register_user,
    )
except Exception as _auth_err:  # Attempt self-heal (install passlib) then retry
    AUTH_IMPORT_ERROR = _auth_err
    try:
        # Try installing passlib if missing; ignore result
        _pip_install_if_missing(["passlib[bcrypt]>=1.7.4"])  # best effort
        import importlib, importlib.util
        mod = None
        try:
            # First, try importing by module name (may resolve to third-party 'auth')
            mod = importlib.import_module("auth")
        except Exception:
            mod = None
        # If imported module doesn't have expected attributes, try loading local file explicitly
        if not mod or not hasattr(mod, "authenticate"):
            auth_path = str(Path(__file__).parent / "auth.py")
            spec = importlib.util.spec_from_file_location("vocalbrand_auth_local", auth_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                except Exception:
                    mod = None
        if not mod:
            raise ImportError("Failed to import local auth module")
        authenticate = getattr(mod, "authenticate")  # type: ignore[misc]
        ensure_demo_user = getattr(mod, "ensure_demo_user")  # type: ignore[misc]
        get_user = getattr(mod, "get_user")  # type: ignore[misc]
        get_free_usage = getattr(mod, "get_free_usage")  # type: ignore[misc]
        increment_free_usage = getattr(mod, "increment_free_usage")  # type: ignore[misc]
        get_minutes_balance = getattr(mod, "get_minutes_balance")  # type: ignore[misc]
        get_setup_credits = getattr(mod, "get_setup_credits")  # type: ignore[misc]
        get_user_by_email = getattr(mod, "get_user_by_email")  # type: ignore[misc]
        hash_backend_status = getattr(mod, "hash_backend_status")  # type: ignore[misc]
        init_db = getattr(mod, "init_db")  # type: ignore[misc]
        register_user = getattr(mod, "register_user")  # type: ignore[misc]
        AUTH_IMPORT_ERROR = None
    except Exception as _auth_err2:  # Final fallback: define stubs which raise clear error on call
        AUTH_IMPORT_ERROR = _auth_err2
        def _fail(*_a, **_k):
            raise RuntimeError(f"Auth module failed to import: {_auth_err2}")
        authenticate = _fail  # type: ignore[assignment]
        ensure_demo_user = lambda: None  # type: ignore[assignment]
        get_user = _fail  # type: ignore[assignment]
        get_free_usage = _fail  # type: ignore[assignment]
        increment_free_usage = _fail  # type: ignore[assignment]
        get_minutes_balance = _fail  # type: ignore[assignment]
        get_setup_credits = _fail  # type: ignore[assignment]
        get_user_by_email = _fail  # type: ignore[assignment]
        hash_backend_status = _fail  # type: ignore[assignment]
        init_db = lambda: None  # type: ignore[assignment]
        register_user = _fail  # type: ignore[assignment]
from engine import DEFAULT_MODEL_ID, DEFAULT_OUTPUT_FORMAT, VocalBrandEngine
from payment import PaymentManager
from utils.audio_utils import validate_audio_bytes, quality_score
from utils.ffmpeg_auto import attempt_auto_ffmpeg
from utils.ui import inject_css, inject_mobile_nav_helpers
from utils.email_utils import send_contact_email, is_email_configured
from utils.seo import inject_seo_meta

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vocalbrand.app")

FREE_LIMIT = int(os.getenv("VOCALBRAND_FREE_LIMIT", "3"))
BRIDGE_HISTORY_LIMIT = int(os.getenv("VOCALBRAND_BRIDGE_HISTORY_LIMIT", "25"))
BRIDGE_QUEUE: "queue.Queue[str]" = queue.Queue()

# Ensure recorder components are present on Streamlit Cloud before proceeding.
try:
    ensure_native_recorder_available()
    logger.info(
        "Recorder availability after auto-install: audiorecorder=%s, st_audiorec=%s, mic_recorder=%s",
        audiorecorder is not None,
        st_audiorec is not None,
        'mic_recorder' in globals() and (mic_recorder is not None),
    )
except Exception as _e:
    logger.warning("Auto-install for recorder components skipped or failed: %s", _e)
def handle_billing_return() -> None:
    """If redirected back from Stripe, verify session and flip subscription flag.

    Supports success and cancel flows via query params added by PaymentManager.
    """
    try:
        params = st.query_params  # Streamlit 1.30+
        billing = params.get("billing")
        sess_id = params.get("session_id")
    except Exception:
        billing = None
        sess_id = None
    if not billing:
        return
    if billing == "success" and sess_id and payment_manager:
        # Attempt to fetch session details (covers subscription and one-time payments)
        try:
            summary = payment_manager.get_line_items_summary(str(sess_id))
        except Exception:
            summary = None

        # Subscription activation path if created via in-app checkout
        try:
            sub_id = payment_manager.get_subscription_id_from_session(str(sess_id))
        except Exception:
            sub_id = None
        if sub_id and st.session_state.get("user_id"):
            try:
                from auth import set_subscription
                set_subscription(st.session_state["user_id"], True, stripe_sub_id=sub_id)
                st.session_state["subscription_active"] = True
                st.success("Subscription activated! 🎉")
            except Exception:
                st.session_state["subscription_active"] = True

        # One-time entitlements (Payment Links or one-off payments)
        try:
            if summary and summary.get("mode") == "payment":
                from auth import (
                    add_minutes_balance,
                    add_setup_credits,
                    get_user_by_email,
                    has_processed_session,
                    mark_processed_session,
                )
                # Resolve user: prefer logged-in; else match by email from checkout
                uid = st.session_state.get("user_id")
                if not uid:
                    email = summary.get("customer_email")
                    if email:
                        u = get_user_by_email(str(email))
                        uid = u.get("id") if u else None
                if uid:
                    if not has_processed_session(str(sess_id)):
                        minutes_added = 0
                        setup_added = 0
                        for item in summary.get("items", []) or []:
                            price_id = item.get("price_id")
                            qty = int(item.get("quantity") or 1)
                            grant = ENTITLEMENT_MAP.get(price_id or "")
                            if not grant:
                                continue
                            if grant.get("minutes"):
                                minutes_added += int(grant["minutes"]) * qty
                            if grant.get("setup"):
                                setup_added += int(grant["setup"]) * qty
                        if minutes_added > 0:
                            new_min = add_minutes_balance(int(uid), minutes_added)
                            st.success(f"Minutes pack activated: +{minutes_added} min (now {new_min})")
                        if setup_added > 0:
                            new_sc = add_setup_credits(int(uid), setup_added)
                            st.success(f"Setup credit added: +{setup_added} (now {new_sc})")
                        mark_processed_session(int(uid), str(sess_id), kind="payment", amount_cents=summary.get("amount_total"), currency=summary.get("currency"))
                    else:
                        st.info("Payment already processed. Your credits are up to date.")
                else:
                    st.warning("Payment received but cannot match to an account. Please sign in with the same email and refresh.")
        except Exception as e:
            st.warning(f"Post-payment processing note: {e}")

        # Clean query params and refresh
        try:
            st.query_params.clear()
        except Exception:
            pass
        safe_rerun(0.2)
    elif billing == "cancel":
        st.info("Checkout canceled. You can try again anytime.")
        try:
            st.query_params.clear()
        except Exception:
            pass


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch secrets from environment variables or local TOML files."""
    if key in os.environ:
        return os.environ[key]
    for candidate in ("secrets.toml", "secrets.example.toml"):
        path = Path(candidate)
        if not path.exists():
            continue
        try:
            import tomllib  # type: ignore

            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(data.get(key), str):
            return data[key]
        for section in ("default", "secrets"):
            section_data = data.get(section)
            if isinstance(section_data, dict) and isinstance(section_data.get(key), str):
                return section_data[key]
    return default


def safe_rerun(delay: float | None = None) -> None:
    """Compatibility wrapper around Streamlit rerun APIs."""
    if delay:
        time.sleep(delay)
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        else:  # pragma: no cover
            st.experimental_rerun()
    except Exception:  # noqa: BLE001
        logger.debug("rerun swallow", exc_info=True)


@dataclass
class BridgeState:
    """Recorder bridge state shared between browser component and app."""

    lock: threading.Lock = field(default_factory=threading.Lock)
    latest: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    hits: int = 0

    def push(self, payload: Dict[str, Any]) -> None:
        with self.lock:
            self.latest = payload
            self.history.append(payload)
            if len(self.history) > BRIDGE_HISTORY_LIMIT:
                self.history.pop(0)
            self.hits += 1

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return dict(self.latest)


BRIDGE_STATE = BridgeState()


def _resolve_binary(name: str, env_key: str | None = None) -> Optional[str]:
    env_candidate = os.getenv(env_key or name.upper())
    if env_candidate and Path(env_candidate).exists():
        return env_candidate
    return shutil.which(name)


def _scan_local_ffmpeg() -> Tuple[str, str]:
    """Search project tree for bundled ffmpeg/ffprobe binaries if not on PATH.

    We purposely keep this lightweight (no heavy recursion limit) and only
    look a few levels deep to avoid large latency on first page load.
    """
    root = Path(__file__).parent
    # Common nested vendor folder patterns
    candidate_dirs = [root, root / "ffmpeg", root / "ffmpeg-2025-09-28-git-0fdb5829e3-full_build"]
    # Include any *ffmpeg* folders at depth 2
    for p in root.glob("*ffmpeg*/**/bin"):
        candidate_dirs.append(p)
    ffmpeg_path = ""
    ffprobe_path = ""
    # Support both Windows (.exe) and Linux (no extension)
    ffmpeg_names = ["ffmpeg.exe", "ffmpeg"]
    ffprobe_names = ["ffprobe.exe", "ffprobe"]
    
    for d in candidate_dirs:
        if not d.exists():
            continue
        # Try to find ffmpeg
        for fname in ffmpeg_names:
            fp = d / fname
            if fp.exists():
                ffmpeg_path = str(fp)
                break
        # Try to find ffprobe
        for fname in ffprobe_names:
            fp2 = d / fname
            if fp2.exists():
                ffprobe_path = str(fp2)
                break
        if ffmpeg_path and ffprobe_path:
            break
    return ffmpeg_path, ffprobe_path


def initialize_recorder_support() -> Tuple[bool, str, str, str, str]:
    attempt_auto_ffmpeg()
    
    # Try to find ffmpeg using multiple methods
    ffmpeg_path = _resolve_binary("ffmpeg", "FFMPEG_BINARY") or ""
    ffprobe_path = _resolve_binary("ffprobe", "FFPROBE_BINARY") or ""
    
    logger.info("FFmpeg detection attempt 1 (PATH/env): ffmpeg=%s, ffprobe=%s", ffmpeg_path, ffprobe_path)
    
    if not ffmpeg_path or not ffprobe_path:
        local_ffmpeg, local_ffprobe = _scan_local_ffmpeg()
        ffmpeg_path = ffmpeg_path or local_ffmpeg
        ffprobe_path = ffprobe_path or local_ffprobe
        logger.info("FFmpeg detection attempt 2 (local scan): ffmpeg=%s, ffprobe=%s", ffmpeg_path, ffprobe_path)
    
    if ffmpeg_path:
        os.environ.setdefault("FFMPEG_BINARY", ffmpeg_path)
        # Prepend bin directory to PATH for libraries (pydub) relying on PATH scan
        bin_dir = str(Path(ffmpeg_path).parent)
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        logger.info("FFmpeg configured: FFMPEG_BINARY=%s, PATH updated with %s", ffmpeg_path, bin_dir)
    if ffprobe_path:
        os.environ.setdefault("FFPROBE_BINARY", ffprobe_path)
        logger.info("FFprobe configured: FFPROBE_BINARY=%s", ffprobe_path)
    
    recorder_message = ""
    status = "ok"
    # Treat mic_recorder as a valid native component too (Cloud-friendly)
    has_component = (audiorecorder is not None) or (st_audiorec is not None) or (
        'mic_recorder' in globals() and (mic_recorder is not None)
    )
    
    logger.info(
        "Audio recorder components: audiorecorder=%s, st_audiorec=%s, mic_recorder=%s",
        audiorecorder is not None,
        st_audiorec is not None,
        'mic_recorder' in globals() and (mic_recorder is not None),
    )
    
    if not has_component:
        status = "component_missing"
        recorder_message = (
            "Install recorder: pip install streamlit-audiorecorder  (inside your venv). "
            "Or: pip install streamlit-audio-recorder. "
            "Imports: 'from audiorecorder import audiorecorder' or 'from streamlit_audio_recorder import st_audiorec'."
        )
        logger.error("Audio recorder component missing!")
    elif not ffmpeg_path:
        status = "ffmpeg_missing"
        recorder_message = "FFmpeg not detected. Place binaries under project /ffmpeg.../bin or add to PATH."
        logger.error("FFmpeg binary not found in PATH or local directories!")
    
    logger.info(
        "Recorder init | component=%s status=%s ffmpeg=%s ffprobe=%s path_in_env=%s",
        has_component,
        status,
        ffmpeg_path,
        ffprobe_path,
        os.environ.get("FFMPEG_BINARY"),
    )
    comp = (
        "audiorecorder"
        if audiorecorder is not None
        else ("st_audiorec" if st_audiorec is not None else ("mic_recorder" if ('mic_recorder' in globals() and mic_recorder is not None) else "none"))
    )
    msg = recorder_message or f"component={comp}"
    return has_component and status == "ok", status, ffmpeg_path, ffprobe_path, msg


HAS_NATIVE_RECORDER, RECORDER_STATUS, FFMPEG_PATH, FFPROBE_PATH, RECORDER_MSG = initialize_recorder_support()

ELEVENLABS_KEY = get_secret("ELEVENLABS_API_KEY", os.getenv("ELEVENLABS_API_KEY", "")) or ""

# Initialize voice manager for quota handling
from voice_manager import create_voice_manager
voice_manager = create_voice_manager(ELEVENLABS_KEY)

if voice_manager:
    logger.info("✅ Voice manager initialized successfully - auto-cleanup enabled")
else:
    logger.error("❌ Voice manager NOT initialized - auto-cleanup DISABLED!")

# Initialize engine with voice manager
engine = VocalBrandEngine(ELEVENLABS_KEY, voice_manager=voice_manager)
if engine.offline:
    logger.warning("Engine operating in offline mode (%s)", engine.offline_reason)

STRIPE_KEY = get_secret("STRIPE_API_KEY", os.getenv("STRIPE_API_KEY", "")) or ""
STRIPE_PRICE_ID = get_secret("STRIPE_PRICE_ID")
STRIPE_PRICE_ID_ANNUAL = get_secret("STRIPE_PRICE_ID_ANNUAL")
payment_manager = PaymentManager(
    STRIPE_KEY, 
    price_id=STRIPE_PRICE_ID,
    price_id_annual=STRIPE_PRICE_ID_ANNUAL
) if STRIPE_KEY else None

# Map price IDs (env) to entitlements for one-time purchases
PACK60_PRICE_ID = os.getenv("PACK60_PRICE_ID")
PACK300_PRICE_ID = os.getenv("PACK300_PRICE_ID")
PACK1000_PRICE_ID = os.getenv("PACK1000_PRICE_ID")
SETUP_PRO_PRICE_ID = os.getenv("SETUP_PRO_PRICE_ID")
SETUP_ENT_PRICE_ID = os.getenv("SETUP_ENT_PRICE_ID")

ENTITLEMENT_MAP: Dict[str, Dict[str, int]] = {}
if PACK60_PRICE_ID:
    ENTITLEMENT_MAP[PACK60_PRICE_ID] = {"minutes": 60}
if PACK300_PRICE_ID:
    ENTITLEMENT_MAP[PACK300_PRICE_ID] = {"minutes": 300}
if PACK1000_PRICE_ID:
    ENTITLEMENT_MAP[PACK1000_PRICE_ID] = {"minutes": 1000}
if SETUP_PRO_PRICE_ID:
    ENTITLEMENT_MAP[SETUP_PRO_PRICE_ID] = {"setup": 1}
if SETUP_ENT_PRICE_ID:
    ENTITLEMENT_MAP[SETUP_ENT_PRICE_ID] = {"setup": 1}

SESSION_DEFAULTS: Dict[str, Any] = {
    "user_id": None,
    "user_email": None,
    "user_is_admin": os.getenv("ADMIN_MODE") == "1",
    "subscription_active": False,
    "nav_page": "Onboarding",
    "clone_voice_id": "",
    "clone_voice_label": "",
    "clone_status": "",
    "clone_timestamp": "",
    "clone_history": [],
    "tts_history": [],
    "pending_audio_bytes": b"",
    "pending_audio_label": "",
    "pending_audio_meta": {},
    "latest_checkout_id": None,
    # UX and automation toggles
    "use_pro_recorder": False,  # Standard recorder by default; user can enable Pro (timer + waveform) via checkbox
    "trim_silence_toggle": False,  # If enabled, trim leading/trailing silence before cloning
    "auto_clone_toggle": False,  # If enabled, auto-clone immediately after recording lock-in
    "last_auto_clone_hash": "",  # To avoid double auto-clone on reruns
}


def configure_page() -> None:
    try:
        # Use logo.png as page icon if available
        icon_path = "logo.png"
        page_icon = icon_path if Path(icon_path).exists() else "🎙️"
        st.set_page_config(
            page_title="VocalBrand Supreme - Clone Your Voice in 30 Seconds | AI Voice Generator",
            page_icon=page_icon,
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                "Get Help": "https://vocalbrand.com/support",
                "Report a bug": "https://vocalbrand.com/bug",
                "About": "VocalBrand Supreme - Transform your voice into a digital asset. Clone once, generate unlimited professional audio in seconds.",
            },
        )
    except Exception:  # pragma: no cover - set_page_config only allowed once
        pass


def ensure_session_defaults() -> None:
    for key, default in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default.copy() if isinstance(default, (list, dict)) else default


def ensure_voice_reset_on_logout() -> None:
    if st.session_state.get("user_id"):
        return
    st.session_state["clone_voice_id"] = ""
    st.session_state["clone_voice_label"] = ""
    st.session_state["clone_status"] = ""
    st.session_state["clone_timestamp"] = ""
    st.session_state["clone_history"] = []
    st.session_state["tts_history"] = []
    st.session_state["pending_audio_bytes"] = b""
    st.session_state["pending_audio_label"] = ""
    st.session_state["pending_audio_meta"] = {}


def logout() -> None:
    st.session_state["user_id"] = None
    st.session_state["user_email"] = None
    st.session_state["subscription_active"] = False
    ensure_voice_reset_on_logout()
    safe_rerun(0.05)


def format_timestamp(ts: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return ts


def _ingest_audio_bytes(raw_bytes: bytes, *, source: str, filename: str | None = None) -> Dict[str, Any]:
    validation = validate_audio_bytes(raw_bytes)
    digest = hashlib.sha1(raw_bytes).hexdigest()[:12]
    quality = quality_score(validation["duration"], validation["loudness_dbfs"]) if validation["ok"] else None
    meta = {
        "source": source,
        "filename": filename or f"{source}_{digest}.wav",
        "hash": digest,
        "ingested_at": datetime.utcnow().isoformat(),
        "quality": quality,
    }
    meta.update({k: v for k, v in validation.items() if k != "raw_bytes"})
    BRIDGE_STATE.push(meta)
    st.session_state["pending_audio_bytes"] = raw_bytes
    st.session_state["pending_audio_label"] = meta["filename"]
    st.session_state["pending_audio_meta"] = meta
    st.session_state["recording_locked_in"] = True
    logger.info(
        "Ingested audio | source=%s hash=%s size=%sB ok=%s duration=%.2fs loudness=%s",
        source,
        digest,
        len(raw_bytes),
        meta.get("ok"),
        meta.get("duration", 0.0),
        meta.get("loudness_dbfs"),
    )
    return meta


def _maybe_trim_silence(raw_bytes: bytes) -> Tuple[bytes, Optional[Dict[str, Any]]]:
    """Optionally trim leading/trailing silence based on user toggle.

    Returns (bytes, info_dict|None). If no trimming applied, returns original bytes and None.
    """
    if not st.session_state.get("trim_silence_toggle"):
        return raw_bytes, None
    try:
        from pydub import AudioSegment  # type: ignore
        from pydub.silence import detect_nonsilent  # type: ignore
        seg = AudioSegment.from_file(BytesIO(raw_bytes))
        dur_ms = len(seg)
        # Conservative silence threshold and window
        # Users in noisy rooms: raise threshold (less negative)
        thresh = -40  # dBFS
        window = 20  # ms
        non_silent = detect_nonsilent(seg, min_silence_len=window, silence_thresh=thresh)
        if not non_silent:
            return raw_bytes, {"applied": False, "reason": "all_silent"}
        start = max(0, non_silent[0][0] - 20)
        end = min(dur_ms, non_silent[-1][1] + 20)
        if end <= start:
            return raw_bytes, {"applied": False, "reason": "invalid_bounds"}
        trimmed = seg[start:end]
        out = BytesIO()
        trimmed.export(out, format="wav")
        return out.getvalue(), {
            "applied": True,
            "orig_ms": dur_ms,
            "trimmed_ms": len(trimmed),
            "removed_ms": max(0, dur_ms - len(trimmed)),
            "threshold_dbfs": thresh,
        }
    except Exception as e:  # noqa: BLE001
        logger.warning("Silence trim failed: %s", e)
        return raw_bytes, {"applied": False, "reason": str(e)}


def render_file_upload_fallback() -> None:
    st.markdown("#### Or upload a studio sample")
    uploaded = st.file_uploader(
        "Upload WAV, MP3, or M4A", type=["wav", "mp3", "m4a", "aac"], key="clone_file_upload"
    )
    if not uploaded:
        return
    raw_bytes = uploaded.read()
    if not raw_bytes:
        st.warning("Uploaded file appears empty.")
        return
    meta = _ingest_audio_bytes(raw_bytes, source="upload", filename=uploaded.name)
    _render_audio_feedback(meta, raw_bytes)


def render_audio_capture_area() -> None:
    st.markdown("#### Record a 30-60s sample")
    # Allow forcing Pro Recorder (HTML5) even if native is present, for live timer+waveform
    force_pro = bool(st.session_state.get("use_pro_recorder"))
    # If Pro is forced, or if native is missing AND we also don't have mic_recorder,
    # render the HTML5 Pro fallback. If mic_recorder exists, we'll skip this and use it below.
    if force_pro or (not HAS_NATIVE_RECORDER and not ('mic_recorder' in globals() and mic_recorder is not None)):
        st.info(
            (
                "Using Pro Recorder (live timer + waveform).\n\n"
                "Tip: If the sample doesn’t auto-appear below, click ‘Download recording’ and then upload it in the drop zone to proceed."
            )
            if force_pro
            else (
                "Native recorder unavailable: %s. Using built-in HTML5 fallback (refresh if permissions denied).\n\n"
                "Tip: If the sample doesn’t auto-appear below, click ‘Download recording’ and then upload it in the drop zone to proceed."
            )
            % (RECORDER_MSG or "component missing"),
            icon="ℹ️",
        )
        # Fallback with direct base64 injection + live loudness/duration estimation
        fallback_id = "fallback_recorder"
        js_template = """
<div id="__FALLBACK_ID__"></div>
<script>
(function(){
    const rootId = "__FALLBACK_ID__";
    function init(){
        const container = document.getElementById(rootId);
        if (!container) { setTimeout(init, 50); return; }
        if (container.dataset.vbInit === '1') return;
        container.dataset.vbInit = '1';
        container.innerHTML = `
            <style>
              /* Scope styles to this component only - SUPREME LIGHT THEME */
              #${rootId} .vbrec-toolbar { display:flex; gap:0.75rem; align-items:center; flex-wrap:wrap; justify-content:center; margin-bottom:1rem; }
              #${rootId} .vbrec-btn { 
                padding:0.75rem 1.5rem; 
                border:none; 
                border-radius:10px; 
                font-weight:600; 
                cursor:pointer; 
                transition:all 0.3s ease;
                min-width:140px;
                font-size:1rem;
                box-shadow:0 4px 6px rgba(0,0,0,0.1);
                display:inline-flex;
                align-items:center;
                justify-content:center;
                gap:0.5rem;
              }
              #${rootId} .vbrec-btn--start { 
                background: linear-gradient(135deg,#1a365d 0%, #2d3748 100%); 
                color:#ffffff; 
              }
              #${rootId} .vbrec-btn--start:hover:not(:disabled) { 
                background: linear-gradient(135deg,#2d3748 0%, #1a365d 100%); 
                transform:translateY(-2px);
                box-shadow:0 8px 12px rgba(0,0,0,0.15);
              }
              #${rootId} .vbrec-btn--stop { 
                background:linear-gradient(135deg,#ef4444 0%, #dc2626 100%); 
                color:#ffffff;
                box-shadow:0 4px 6px rgba(239,68,68,0.2);
              }
              #${rootId} .vbrec-btn--stop:hover:not(:disabled) {
                background:linear-gradient(135deg,#dc2626 0%, #ef4444 100%);
                transform:translateY(-2px);
                box-shadow:0 8px 12px rgba(239,68,68,0.3);
              }
              #${rootId} .vbrec-btn:disabled { opacity:0.6; cursor:not-allowed; transform:none; }
              #${rootId} #vb_status { 
                font-size:0.95rem; 
                color:#0f172a; 
                font-weight:600;
                padding:0.5rem 1rem;
                background:#f8fafc;
                border-radius:8px;
              }
              #${rootId} #vb_level { 
                font-size:0.95rem; 
                color:#0f172a; 
                font-weight:600;
                padding:0.5rem 1rem;
                background:#f8fafc;
                border-radius:8px;
              }
              #${rootId} #vb_canvas { 
                margin-top:1rem; 
                width:100%; 
                height:64px; 
                background:#e2e8f0; 
                border:2px solid #cbd5e1;
                border-radius:8px; 
                box-shadow:inset 0 2px 4px rgba(0,0,0,0.05);
              }
              #${rootId} #vb_download_wrap { 
                margin-top:1rem; 
                text-align:center; 
              }
              #${rootId} #vb_download_wrap a { 
                display:inline-flex;
                align-items:center;
                gap:0.5rem;
                background:#e2e8f0;
                color:#1a365d; 
                padding:0.75rem 1.5rem;
                border-radius:10px;
                text-decoration:none;
                font-weight:600; 
                border:2px solid #94a3b8;
                transition:all 0.3s ease;
                box-shadow:0 2px 6px rgba(0,0,0,0.05);
              }
              #${rootId} #vb_download_wrap a:hover {
                background:#cbd5e1;
                border-color:#1a365d;
                transform:translateY(-2px);
                box-shadow:0 4px 12px rgba(0,0,0,0.1);
              }
            </style>
            <div class="vbrec-toolbar">
                <button id="vb_start" class="vbrec-btn vbrec-btn--start">🎙️ Start</button>
                <button id="vb_stop" class="vbrec-btn vbrec-btn--stop" disabled>⏹️ Stop</button>
                <span id="vb_status">Idle</span>
                <span id="vb_level">Level: -- dB | 0.0s</span>
            </div>
            <canvas id="vb_canvas" width="600" height="64"></canvas>
            <audio id="vb_play" controls style="margin-top:1rem;width:100%;display:none;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:0.5rem;"></audio>
            <div id="vb_download_wrap" style="display:none;"><a id="vb_download" download="vocalbrand_recording.webm">⬇️ Download recording</a></div>
        `;
        const statusEl = container.querySelector('#vb_status');
        const levelEl = container.querySelector('#vb_level');
        const startBtn = container.querySelector('#vb_start');
        const stopBtn = container.querySelector('#vb_stop');
        const audioEl = container.querySelector('#vb_play');
        const canvas = container.querySelector('#vb_canvas');
        const ctx = canvas.getContext('2d');
        let mediaRecorder, chunks=[], analyser, dataArray, rafId, startedAt=0;
        function log(m){ statusEl.textContent = m; }
        function postHeight(){
            try{ window.parent.postMessage({isStreamlitMessage:true, type:'streamlit:setFrameHeight', height: document.body.scrollHeight }, '*'); }catch(e){}
        }
        function postReady(){
            try{ window.parent.postMessage({isStreamlitMessage:true, type:'streamlit:componentReady'}, '*'); }catch(e){}
        }
        function postValue(val){
            try{ window.parent.postMessage({isStreamlitMessage:true, type:'streamlit:setComponentValue', value: val}, '*'); }catch(e){}
        }
        function meter(){
            if(!analyser) return;
            analyser.getByteTimeDomainData(dataArray);
            let peak=0; for(let i=0;i<dataArray.length;i++){ const v=(dataArray[i]-128)/128; const a=Math.abs(v); if(a>peak) peak=a; }
            const db = (peak>0)? (20*Math.log10(peak)).toFixed(1) : '-inf';
            const elapsed = ((performance.now()-startedAt)/1000).toFixed(1);
            levelEl.textContent = `Level: ${db} dB | ${elapsed}s`;
            // Draw waveform
            const W = canvas.width, H = canvas.height;
            ctx.fillStyle = '#e2e8f0'; ctx.fillRect(0,0,W,H);
            ctx.strokeStyle = '#1a365d'; ctx.lineWidth = 2; ctx.beginPath();
            for(let x=0; x<W; x++){
                const i = Math.floor(x / W * dataArray.length);
                const v = (dataArray[i]-128)/128;
                const y = H/2 - v * (H/2 - 4);
                if(x===0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }
            ctx.stroke();
            rafId = requestAnimationFrame(meter);
        }
        startBtn.onclick = async ()=>{
            try{
                const stream = await navigator.mediaDevices.getUserMedia({audio:true});
                const actx = new (window.AudioContext||window.webkitAudioContext)();
                const src = actx.createMediaStreamSource(stream);
                analyser = actx.createAnalyser(); analyser.fftSize=1024;
                dataArray = new Uint8Array(analyser.fftSize);
                src.connect(analyser);
                // Initialize MediaRecorder and capture chunks (PRO RECORDER — LIGHT THEME)
                chunks = [];
                try {
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
                } catch(e) {
                    // Fallback without mimeType if browser rejects the option
                    mediaRecorder = new MediaRecorder(stream);
                }
                mediaRecorder.ondataavailable = (ev)=>{ if (ev.data && ev.data.size) { chunks.push(ev.data); } };
                mediaRecorder.onstop = async ()=>{
                    cancelAnimationFrame(rafId);
                    const blob = new Blob(chunks,{type:'audio/webm'});
                    const ab = await blob.arrayBuffer();
                    const bytes = new Uint8Array(ab);
                    let binary=''; for(let i=0;i<bytes.length;i++) binary += String.fromCharCode(bytes[i]);
                    const b64 = btoa(binary);
                    const url = URL.createObjectURL(blob);
                    audioEl.src = url; audioEl.style.display='block';
                    const dw = container.querySelector('#vb_download_wrap');
                    const dl = container.querySelector('#vb_download');
                    if (dw && dl) { dw.style.display='block'; dl.href = url; }
                    statusEl.textContent = 'Captured ' + (bytes.length/1000).toFixed(1) + ' kB';
                    // Also write to a hidden textbox in the parent DOM if available (data URL)
                    try{
                        const ta = window.parent.document.querySelector('textarea[data-testid="stTextArea"]#pro_recorder_payload');
                        if(ta){ ta.value = 'data:audio/webm;base64,' + b64; ta.dispatchEvent(new Event('input',{bubbles:true})); }
                    }catch(e){}
                    postValue({b64: b64, size: bytes.length});
                    postHeight();
                };
                mediaRecorder.start(); startedAt = performance.now(); log('Recording...');
                startBtn.disabled=true; stopBtn.disabled=false; meter();
            }catch(err){ log('Error: '+err.message); }
        };
        stopBtn.onclick=()=>{ if(mediaRecorder && mediaRecorder.state!=='inactive') mediaRecorder.stop(); startBtn.disabled=false; stopBtn.disabled=true; log('Processing...'); };
        postReady(); postHeight();
    }
    init();
})();
</script>
    """
        # Capture value posted back from the HTML component (via postMessage streamlit:setComponentValue)
        pro_component_val = st.components.v1.html(
            js_template.replace("__FALLBACK_ID__", fallback_id),
            height=260,
            scrolling=False,
        )
        st.caption(
            "Pro Recorder provides live timing + waveform. After stopping, a ‘Download recording’ link appears; if auto‑ingest doesn’t trigger, download and upload the file below to continue."
        )
        # Hidden receiver for data URL (data:audio/webm;base64,....) — kept invisible
        pro_val = st.text_input(
            "pro_recorder_b64_hidden",
            key="pro_recorder_payload",
            label_visibility="collapsed",
        )
        last_hash_key = "last_fallback_b64_hash"
        # Prefer direct component value; fallback to hidden textarea if needed
        b64_from_component: Optional[str] = None
        if isinstance(pro_component_val, dict) and pro_component_val.get("b64"):
            try:
                size = int(pro_component_val.get("size") or 0)
            except Exception:
                size = 0
            # basic sanity: accept if > 1KB
            if size > 1024:
                b64_from_component = str(pro_component_val["b64"])  # plain base64 without data URL prefix
        if b64_from_component:
            pro_val = "data:audio/webm;base64," + b64_from_component
        if pro_val:
            try:
                # Accept data URL or plain base64
                b64 = pro_val
                if b64.startswith("data:"):
                    b64 = b64.split(",", 1)[1]
                current_hash = hashlib.sha1(b64.encode("utf-8")).hexdigest()
                auto_needed = st.session_state.get(last_hash_key) != current_hash
                force = st.button("Use Recording (Pro)", key="use_recording_pro_btn")
                if auto_needed or force:
                    raw_webm = base64.b64decode(b64)
                    from pydub import AudioSegment  # type: ignore
                    seg = AudioSegment.from_file(BytesIO(raw_webm), format="webm")
                    wav_buf = BytesIO()
                    seg.export(wav_buf, format="wav")
                    wav_bytes = wav_buf.getvalue()
                    meta = _ingest_audio_bytes(wav_bytes, source="pro_recorder", filename="recording.wav")
                    _render_audio_feedback(meta, wav_bytes)
                    st.session_state[last_hash_key] = current_hash
                    st.success("Recording Locked In ✅", icon="✅")
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if len(msg) > 220:
                    msg = msg[:220] + "…"
                st.warning(f"Pro Recorder decode failed: {msg}")
        # Show upload option and prevent further rendering when this Pro fallback is active
        render_file_upload_fallback()
        return
    # Prefer st_audiorec if available; it returns raw wav bytes directly
    raw_bytes: Optional[bytes] = None
    if st_audiorec is not None:
        with st.spinner("Ready. Click microphone to start/stop"):
            wav_data = st_audiorec()  # returns bytes or None
        if wav_data:
            raw_bytes = wav_data
    elif audiorecorder is not None:
        audio = audiorecorder(
            "🎙️ Start recording",
            "⏹️ Stop recording",
            key="native_recorder_component",
        )
        if audio and len(audio) > 0:
            buffer = BytesIO()
            audio.export(buffer, format="wav")
            raw_bytes = buffer.getvalue()
    elif mic_recorder is not None:
        # mic_recorder returns a dict with 'bytes' (wav) when finished
        st.caption("Alternative recorder active (mic_recorder)")
        rec = mic_recorder(start_prompt="🎙️ Start", stop_prompt="⏹️ Stop", just_once=True, use_container_width=True, key="mr_fallback")
        if isinstance(rec, dict) and rec.get("bytes"):
            raw_bytes = rec["bytes"]

    if raw_bytes:
        meta = _ingest_audio_bytes(raw_bytes, source="native_recorder")
        _render_audio_feedback(meta, raw_bytes)
    render_file_upload_fallback()


def _render_audio_feedback(meta: Dict[str, Any], raw_bytes: bytes) -> None:
    if meta.get("ok"):
        st.success("Sample captured and validated ✅")
    else:
        st.warning(meta.get("message", "Audio validation warning"))
    st.audio(raw_bytes, format="audio/wav")
    # Brief summary line
    dur = meta.get("duration")
    loud = meta.get("loudness_dbfs")
    qual = meta.get("quality", {})
    if dur is not None:
        st.caption(f"Duration: {dur:.1f}s | Loudness: {loud:.1f} dBFS" if isinstance(loud, (int, float)) else f"Duration: {dur:.1f}s")
    # Post-capture waveform visualization (downsampled)
    try:
        import numpy as np  # type: ignore
        from pydub import AudioSegment  # type: ignore
        seg = AudioSegment.from_file(BytesIO(raw_bytes))
        arr = np.array(seg.get_array_of_samples())
        if seg.channels > 1:
            arr = arr.reshape((-1, seg.channels)).mean(axis=1)
        # Downsample to ~1200 points for light plotting
        target = 1200
        if len(arr) > target:
            step = len(arr) // target
            arr = arr[: target * step]
            arr = arr.reshape(-1, step).mean(axis=1)
        # Normalize to [-1, 1] for cleaner axis
        maxv = float(np.max(np.abs(arr))) or 1.0
        arr = (arr / maxv).astype("float32")
        st.line_chart(arr, height=120)
    except Exception:
        pass
    if os.getenv("DEBUG_LOGGING", "0") == "1":
        with st.expander("Sample diagnostics", expanded=False):
            safe_meta = {k: v for k, v in meta.items() if k not in {"raw_bytes"}}
            st.json(json.loads(json.dumps(safe_meta, default=str)))


def render_clone_section() -> None:
    st.subheader("Voice cloning")
    # Visual-only note (policy, not enforced by code)
    st.caption(
        "Usage policy: Pro includes 30 TTS minutes/month. Additional usage via Minutes Packs (sold by Payment Links)."
    )
    # Power-user controls
    colx, coly, colz = st.columns([1.2, 1.2, 1])
    with colx:
        st.checkbox("Use Pro Recorder (timer + waveform)", key="use_pro_recorder", value=False)
    with coly:
        st.checkbox("Trim silence before cloning", key="trim_silence_toggle")
    with colz:
        st.checkbox("Auto-clone after lock-in", key="auto_clone_toggle")

    render_audio_capture_area()
    meta = st.session_state.get("pending_audio_meta")
    raw_bytes = st.session_state.get("pending_audio_bytes", b"")
    if not raw_bytes:
        st.info("Provide a recording or upload a file to proceed.")
        return
    voice_label_default = st.session_state.get("clone_voice_label") or "My VocalBrand Voice"
    voice_label = st.text_input("Voice label", value=voice_label_default, key="clone_voice_label_input")
    col1, col2 = st.columns([2, 1])
    with col1:
        disabled = not meta or not meta.get("ok")
        if st.button("Clone voice", type="primary", disabled=disabled):
            # Apply optional silence trimming before send
            bytes_to_send, trim_info = _maybe_trim_silence(raw_bytes)
            buf = BytesIO(raw_bytes)
            if bytes_to_send is not raw_bytes:
                buf = BytesIO(bytes_to_send)
            buf.name = meta.get("filename", "voice.wav")
            with st.spinner("Contacting ElevenLabs..."):
                result = engine.clone_voice(buf, voice_label.strip() or "VocalBrand Voice")
            
            # CRITICAL: Only save voice_id if cloning was actually successful
            if result.get("success") and result.get("voice_id"):
                st.session_state["clone_voice_id"] = result.get("voice_id")
                st.session_state["clone_voice_label"] = voice_label
                st.session_state["clone_status"] = result.get("message", "")
                st.session_state["clone_timestamp"] = datetime.utcnow().isoformat()
                history = st.session_state.get("clone_history", [])
                history.append(
                    {
                        "voice_id": result.get("voice_id"),
                        "label": voice_label,
                        "provider": result.get("provider"),
                        "message": result.get("message"),
                        "at": st.session_state["clone_timestamp"],
                        "trim": trim_info,
                    }
                )
                st.session_state["clone_history"] = history[-15:]
                st.success(f"✅ Voice cloned successfully! ID: {result.get('voice_id')}")
            else:
                # CRITICAL: Clear any previous voice_id on failure
                st.session_state["clone_voice_id"] = ""
                st.session_state["clone_status"] = ""
                
                error_msg = result.get("message", "Voice cloning failed")
                error_detail = result.get("error_detail", "")
                provider = result.get("provider", "unknown")
                
                st.error(f"❌ **Voice Cloning Failed**\n\n{error_msg}")
                
                if error_detail:
                    with st.expander("🔍 Technical Details"):
                        st.code(error_detail)
                
                # Provide actionable feedback based on error type
                if provider == "quota_exceeded":
                    st.info(
                        "**Voice Quota Limit Reached**\n\n"
                        "The system automatically attempted to clean up old voices and retry, "
                        "but the operation still failed. This means:\n\n"
                        "- You may have reached your ElevenLabs plan limit\n"
                        "- Try again in a moment (automatic cleanup may need time)\n"
                        "- Consider upgrading your ElevenLabs plan for more voice slots"
                    )
                else:
                    st.warning(
                        "**What to try:**\n"
                        "- Ensure audio is at least 30 seconds long\n"
                        "- Speak clearly in a quiet environment\n"
                        "- Check microphone quality\n"
                        "- Try recording again with better audio quality\n"
                        "- Verify your ElevenLabs API key is valid"
                    )
    with col2:
        if st.button("Discard sample", key="discard_sample_btn"):
            st.session_state["pending_audio_bytes"] = b""
            st.session_state["pending_audio_meta"] = {}
            st.session_state["pending_audio_label"] = ""
            st.info("Sample cleared.")

    # Auto-clone right after lock-in (idempotent)
    if (
        st.session_state.get("auto_clone_toggle")
        and st.session_state.get("recording_locked_in")
        and meta
        and meta.get("hash")
        and st.session_state.get("last_auto_clone_hash") != meta.get("hash")
        and meta.get("ok")
    ):
        voice_label_aut = (st.session_state.get("clone_voice_label") or voice_label_default).strip() or "VocalBrand Voice"
        bytes_to_send, trim_info = _maybe_trim_silence(raw_bytes)
        buf = BytesIO(bytes_to_send)
        buf.name = meta.get("filename", "voice.wav")
        with st.spinner("Auto-cloning with ElevenLabs..."):
            result = engine.clone_voice(buf, voice_label_aut)
        
        # CRITICAL: Only save voice_id if cloning was actually successful
        if result.get("success") and result.get("voice_id"):
            st.session_state["clone_voice_id"] = result.get("voice_id")
            st.session_state["clone_voice_label"] = voice_label_aut
            st.session_state["clone_status"] = result.get("message", "")
            st.session_state["clone_timestamp"] = datetime.utcnow().isoformat()
            st.session_state["last_auto_clone_hash"] = meta.get("hash")
            history = st.session_state.get("clone_history", [])
            history.append(
                {
                    "voice_id": result.get("voice_id"),
                    "label": voice_label_aut,
                    "provider": result.get("provider"),
                    "message": result.get("message"),
                    "at": st.session_state["clone_timestamp"],
                    "auto": True,
                    "trim": trim_info,
                }
            )
            st.session_state["clone_history"] = history[-15:]
            st.success("Auto-clone complete ✅")
        else:
            st.warning(result.get("message", "Auto-clone failed"))


def render_generation_section() -> None:
    st.subheader("Generate speech")
    # Visual-only note (policy, not enforced by code)
    st.caption(
        "Usage policy: Pro includes 30 TTS minutes/month. Additional usage via Minutes Packs (sold by Payment Links)."
    )
    voice_id = st.session_state.get("clone_voice_id", "")
    
    # CRITICAL: Validate voice_id before allowing generation
    if not voice_id:
        st.warning("⚠️ **Clone a voice before generating audio.**\n\nGo to the Voice Cloning section above to record and clone your voice first.")
        return
    
    # CRITICAL: Validate voice_id format (ElevenLabs IDs are alphanumeric, 20-30 chars)
    if len(voice_id) < 15 or not any(c.isdigit() for c in voice_id) or not any(c.isalpha() for c in voice_id):
        st.error(
            f"❌ **Invalid voice ID detected:** `{voice_id}`\n\n"
            "This usually happens when voice cloning failed but wasn't properly handled.\n\n"
            "**Please re-clone your voice using the Voice Cloning section above.**"
        )
        # Clear the invalid voice ID
        st.session_state["clone_voice_id"] = ""
        if st.button("Clear Invalid Voice & Restart"):
            st.session_state["clone_voice_id"] = ""
            st.session_state["clone_status"] = ""
            st.rerun()
        return
    
    st.caption(f"✅ Voice ID: `{voice_id}`")
    voice_label = st.session_state.get("clone_voice_label", "Your Voice")
    if voice_label:
        st.caption(f"Voice: **{voice_label}**")
    with st.expander("Language tips (i)", expanded=False):
        st.markdown(
            "- For English: use the default model and write clean sentences.\n"
            "- For other languages (Portuguese, Spanish, etc.): switch to 'eleven_multilingual_v2'.\n"
            "- Use correct punctuation (commas, periods, question marks) to shape rhythm and prosody.\n"
            "- Provide text with proper diacritics (e.g., Portuguese accents) for better pronunciation.\n"
            "- If pronunciation drifts, re-clone with a sample in the target language and try again."
        )
    prompt = st.text_area("What should this voice say?", height=180, key="tts_prompt")
    col1, col2 = st.columns(2)
    with col1:
        model_id = st.selectbox("Model", [DEFAULT_MODEL_ID, "eleven_multilingual_v2"], index=0)
    with col2:
        output_format = st.selectbox("Output format", [DEFAULT_OUTPUT_FORMAT, "mp3_44100_192", "wav"], index=0)

    # Use database-based counter for free users (persists across sessions/refreshes)
    user_id = st.session_state.get("user_id")
    used_generations = 0
    if user_id and not st.session_state.get("subscription_active"):
        used_generations = get_free_usage(user_id)
    
    disabled = not prompt.strip()
    if not st.session_state.get("subscription_active"):
        st.info(f"Free plan usage: {used_generations}/{FREE_LIMIT} generations")
        if used_generations >= FREE_LIMIT:
            st.error("Free usage limit reached. Upgrade to continue.")
            disabled = True

    if st.button("Generate speech", type="primary", disabled=disabled):
        with st.spinner("Generating with ElevenLabs..."):
            success, audio_buffer, status = engine.text_to_speech(
                prompt.strip(),
                voice_id,
                model_id=model_id,
                output_format=output_format,
            )
        if not success or not audio_buffer:
            st.error(f"Generation failed: {status}")
            return
        audio_bytes = audio_buffer.getvalue()
        st.audio(audio_bytes, format="audio/mpeg" if "mp3" in output_format else "audio/wav")
        st.download_button(
            "Download audio",
            data=audio_bytes,
            file_name=f"vocalbrand_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{'mp3' if 'mp3' in output_format else 'wav'}",
            mime="audio/mpeg" if "mp3" in output_format else "audio/wav",
        )
        
        # Increment persistent usage counter for free users
        if user_id and not st.session_state.get("subscription_active"):
            increment_free_usage(user_id)
        
        history = st.session_state.get("tts_history", [])
        history.append(
            {
                "prompt": prompt.strip()[:180],
                "voice_id": voice_id,
                "status": status,
                "generated_at": datetime.utcnow().isoformat(),
                "format": output_format,
                "bytes": len(audio_bytes),
            }
        )
        st.session_state["tts_history"] = history[-25:]
        st.success("Audio generated and saved to history.")


def render_upgrade_section(container: Any) -> None:
    # Branded upgrade banner
    container.markdown(
        """
        <div class="vb-banner vb-banner--upgrade" style="background:linear-gradient(135deg, #1a365d 0%, #0b2344 100%); color:#fff; border-radius:16px; padding:1.25rem; border:none; margin-bottom:1rem;">
            <div class="vb-banner__title" style="font-weight:800; font-size:1.2rem; color:#fff; margin-bottom:0.5rem;">Upgrade to VocalBrand Pro</div>
            <div class="vb-banner__sub" style="color:#fff; opacity:0.95;">Unlimited generations • Priority processing • Commercial use</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Feature bullets (kept for clarity/SEO) - styled inline to prevent white artifact boxes
    container.markdown(
        """
        <div style="color:#0f172a; line-height:1.8; margin-bottom:1rem;">
        <strong style="color:#0f172a;">Pro Features:</strong><br>
        • Unlimited voice generations<br>
        • Priority processing<br>
        • Commercial license<br>
        • Advanced voice controls<br>
        • 24/7 premium support
        </div>
        """,
        unsafe_allow_html=True,
    )
    if payment_manager is None:
        container.info("Stripe key missing. Configure STRIPE_API_KEY to enable billing.")
        return
    # Gate behind login
    if not st.session_state.get("user_id"):
        container.info("Log in to start a premium subscription.")
        return
    
    # Main subscription options
    container.markdown("---")
    container.markdown('<div class="vb-section-title">💎 Subscription Plans</div>', unsafe_allow_html=True)
    
    user_ref = f"user_{st.session_state['user_id']}"
    # Ensure annual_link is always defined for later checks
    annual_link: Optional[str] = None
    
    # Monthly subscription (in-app checkout)
    with container.container():
        container.markdown('<div class="vb-section-title" style="font-size:1.15rem;">Monthly Pro</div>', unsafe_allow_html=True)
        container.caption("Unlimited generations, cancel anytime")
        if st.button("€29/mo", key="upgrade_btn_monthly", use_container_width=True):
            url, checkout_id = payment_manager.create_checkout_session(user_ref, plan="monthly")
            st.session_state["latest_checkout_id"] = checkout_id
            st.link_button("Open checkout →", url, type="primary")
        container.markdown("")
    
    # Annual subscription (in-app checkout if price ID configured, otherwise Payment Link)
    if payment_manager.price_id_annual:
        # Use in-app checkout with annual price ID
        with container.container():
            container.markdown('<div class="vb-section-title" style="font-size:1.15rem;">Annual Pro</div>', unsafe_allow_html=True)
            container.caption("Save 17% (€290/year vs €348/year)")
            if st.button("€290/yr", key="upgrade_btn_annual", use_container_width=True):
                url, checkout_id = payment_manager.create_checkout_session(user_ref, plan="annual")
                st.session_state["latest_checkout_id"] = checkout_id
                st.link_button("Open checkout →", url, type="primary")
            container.markdown("")
    else:
        # Fall back to Payment Link if annual price ID not configured
        annual_link = os.getenv("ANNUAL_PAYMENT_LINK")
        if annual_link:
            with container.container():
                container.markdown('<div class="vb-section-title" style="font-size:1.15rem;">Annual Pro</div>', unsafe_allow_html=True)
                container.caption("Save 17% (€290/year vs €348/year)")
                st.link_button("€290/yr →", annual_link, type="primary")
                container.markdown("")
    
    # One-time professional services
    setup_prices = {
        "Setup — Professional": ("€497", SETUP_PRO_PRICE_ID, "60 min"),
        "Setup — Enterprise": ("€997", SETUP_ENT_PRICE_ID, "120 min"),
    }
    visible_setups = [(label, price, price_id, duration) for label, (price, price_id, duration) in setup_prices.items() if price_id]
    
    if visible_setups:
        container.markdown("---")
        container.markdown('<div class="vb-section-title">🚀 Professional Onboarding</div>', unsafe_allow_html=True)
        container.caption("One-time guided setup services for teams and enterprises")
        
        for idx, (label, price, price_id, duration) in enumerate(visible_setups):
            with container.container():
                container.markdown(f'<div class="vb-section-title" style="font-size:1.05rem;">{label}</div>', unsafe_allow_html=True)
                container.caption(f"{duration} guided setup & Q&A")
                if st.button(f"{price} →", key=f"setup_{idx}_{price_id}", type="secondary", use_container_width=True):
                    url, checkout_id = payment_manager.create_checkout_session(user_ref, plan="setup", price_id=price_id, mode="payment")
                    st.session_state["latest_checkout_id"] = checkout_id
                    st.link_button("Open checkout →", url, type="primary")
                container.markdown("")
        # Developer note: if Payment Links are shown but price ID envs are missing, remind to set them
        if os.getenv("DEBUG_LOGGING", "0") == "1":
            missing_envs: List[str] = []
            if any("Professional" in lbl for lbl, _, _, _ in visible_setups) and not (SETUP_PRO_PRICE_ID):
                missing_envs.append("SETUP_PRO_PRICE_ID")
            if any("Enterprise" in lbl for lbl, _, _, _ in visible_setups) and not (SETUP_ENT_PRICE_ID):
                missing_envs.append("SETUP_ENT_PRICE_ID")
            if missing_envs:
                container.caption(
                    "Dev: Set price IDs for automatic entitlements → " + ", ".join(missing_envs)
                )
    
    # Minutes packs for additional usage
    pack_prices = {
        "60 min": ("€89", PACK60_PRICE_ID),
        "300 min": ("€399", PACK300_PRICE_ID),
        "1000 min": ("€1,299", PACK1000_PRICE_ID),
    }
    visible_packs = [(label, price, price_id) for label, (price, price_id) in pack_prices.items() if price_id]
    
    if visible_packs:
        container.markdown("---")
        container.markdown('<div class="vb-section-title">⚡ Additional Minutes Packs</div>', unsafe_allow_html=True)
        container.caption("Premium voice minutes for professional use cases")
        
        for idx, (label, price, price_id) in enumerate(visible_packs):
            with container.container():
                container.markdown(f'<div class="vb-section-title" style="font-size:1.05rem;">Voice Minutes Pack {label}</div>', unsafe_allow_html=True)
                if st.button(f"{price} →", key=f"pack_{idx}_{price_id}", use_container_width=True):
                    url, checkout_id = payment_manager.create_checkout_session(user_ref, plan="pack", price_id=price_id, mode="payment")
                    st.session_state["latest_checkout_id"] = checkout_id
                    st.link_button("Open checkout →", url, type="primary")
                container.markdown("")
        # Developer note for entitlement mapping of packs
        if os.getenv("DEBUG_LOGGING", "0") == "1":
            missing_envs: List[str] = []
            if any(lbl == "60 min" for lbl, _, _ in visible_packs) and not (PACK60_PRICE_ID):
                missing_envs.append("PACK60_PRICE_ID")
            if any(lbl == "300 min" for lbl, _, _ in visible_packs) and not (PACK300_PRICE_ID):
                missing_envs.append("PACK300_PRICE_ID")
            if any(lbl == "1000 min" for lbl, _, _ in visible_packs) and not (PACK1000_PRICE_ID):
                missing_envs.append("PACK1000_PRICE_ID")
            if missing_envs:
                container.caption(
                    "Dev: Set price IDs for automatic entitlements → " + ", ".join(missing_envs)
                )
    
    # Help section
    if visible_setups or visible_packs or annual_link:
        container.markdown("---")
        
        # Critical: explain automatic activation
        container.info(
            "💡 **Automatic Activation:** Credits are added instantly after payment. "
            "All purchases use the same secure checkout flow as Pro subscriptions."
        )
        
        with container.expander("💡 Payment Options FAQ", expanded=False):
            container.markdown(
                """
                **What's included in subscriptions?**
                - Monthly Pro (€29/mo): Unlimited generations, priority processing, commercial license
                - Annual Pro (€290/yr): Same as Monthly, but 17% cheaper (2 months free)
                
                **What are Setup services?**
                - One-time onboarding sessions (not recurring). Video call with our team to help you integrate VocalBrand into your workflow.
                - Professional (€497): 60 min session, best for solo entrepreneurs and small teams
                - Enterprise (€997): 120 min session, best for agencies and larger teams
                
                **What are Minutes Packs?**
                - Additional TTS minutes for billing/accounting purposes.
                - These purchases track usage but don't automatically change in-app quotas while features are locked.
                - For account crediting or custom enterprise pricing, use the Contact page.
                
                **How do I switch between Monthly and Annual?**
                - Cancel your Monthly subscription in Stripe, then purchase Annual via the Payment Link above.
                - Need help with the switch? Visit the Contact page for assistance.
                """
            )
            
            # Add Contact Support button prominently
            if container.button("📧 Contact Support", key="contact_from_faq", use_container_width=True):
                st.session_state["nav_page"] = "Contact"
                safe_rerun()
    
    if st.session_state.get("latest_checkout_id"):
        container.caption(f"Latest checkout: {st.session_state['latest_checkout_id']}")


def render_account_panel() -> None:
    st.sidebar.markdown("## Account")
    if st.session_state.get("user_id"):
        st.sidebar.success(f"Signed in as {st.session_state['user_email']}")
        sub_active = st.session_state.get("subscription_active")
        st.sidebar.markdown(f"**Subscription:** {'Active 💎' if sub_active else 'Free tier'}")
        
        # Show purchased balances
        user_id = st.session_state["user_id"]
        minutes_bal = get_minutes_balance(user_id)
        setup_bal = get_setup_credits(user_id)
        
        if minutes_bal > 0 or setup_bal > 0:
            st.sidebar.markdown("---")
            st.sidebar.markdown("**Your Credits:**")
            if minutes_bal > 0:
                st.sidebar.markdown(f"⚡ Minutes: **{minutes_bal}** min")
            if setup_bal > 0:
                st.sidebar.markdown(f"🚀 Setup credits: **{setup_bal}**")
    
    if st.sidebar.button("Log out", key="logout_btn", use_container_width=True):
        logout()
    else:
        st.sidebar.info("Create an account to unlock cloning and TTS.")
    render_upgrade_section(st.sidebar)
    # Only show system status if DEBUG_LOGGING is explicitly enabled
    if os.getenv("DEBUG_LOGGING", "0") == "1":
        st.sidebar.markdown("---")
        with st.sidebar.expander("System status", expanded=False):
            st.markdown(
                f"- Recorder: {'✅' if HAS_NATIVE_RECORDER else '⚠️'} {RECORDER_STATUS} — {RECORDER_MSG or 'ready'}\n"
                f"- FFmpeg: {FFMPEG_PATH or 'not found'}\n"
                f"- ElevenLabs key: {'configured' if ELEVENLABS_KEY else 'missing'}\n"
                f"- Engine offline: {engine.offline} ({engine.offline_reason})"
            )


def login_section() -> None:
    st.header("Welcome to VocalBrand")
    st.write("Create or log into your account to access cloning and speech generation.")
    tabs = st.tabs(["Sign in", "Create account"])
    with tabs[0]:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign in", type="primary")
            if submitted:
                # CRITICAL: Validate inputs before authentication
                email_stripped = (email or "").strip()
                password_stripped = (password or "").strip()
                
                if not email_stripped:
                    st.error("❌ Email is required. Please enter your email address.")
                    return
                
                if not password_stripped:
                    st.error("❌ Password is required. Please enter your password.")
                    return
                
                if len(email_stripped) < 3 or "@" not in email_stripped:
                    st.error("❌ Invalid email format. Please enter a valid email address.")
                    return
                
                if len(password_stripped) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                    return
                
                ok, uid = authenticate(email_stripped, password_stripped)
                if ok and uid:
                    user = get_user(uid)
                    if user:
                        st.session_state["user_id"] = user["id"]
                        st.session_state["user_email"] = user["email"]
                        st.session_state["subscription_active"] = bool(user.get("subscription_active"))
                        st.success("✅ Signed in successfully.")
                        safe_rerun(0.05)
                        return
                st.error("❌ Invalid credentials. Please check your email and password.")
    with tabs[1]:
        with st.form("register_form"):
            email = st.text_input("Work email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            submitted = st.form_submit_button("Create account", type="primary")
            if submitted:
                # CRITICAL: Validate inputs before registration
                email_stripped = (email or "").strip()
                password_stripped = (password or "").strip()
                
                if not email_stripped:
                    st.error("❌ Email is required. Please enter your email address.")
                    return
                
                if not password_stripped:
                    st.error("❌ Password is required. Please create a password.")
                    return
                
                if len(email_stripped) < 3 or "@" not in email_stripped:
                    st.error("❌ Invalid email format. Please enter a valid email address.")
                    return
                
                if len(password_stripped) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                    return
                
                ok, message = register_user(email_stripped, password_stripped)
                if ok:
                    st.success("✅ Account created. Sign in using your credentials.")
                else:
                    st.warning(f"⚠️ Registration failed: {message}")


def render_metrics_panel() -> None:
    if os.getenv("DEBUG_LOGGING", "0") != "1":
        return
    with st.expander("Diagnostics", expanded=False):
        st.markdown("#### Hash backend")
        st.json(hash_backend_status())
        st.markdown("#### Recorder status")
        st.json(
            {
                "has_native": HAS_NATIVE_RECORDER,
                "status": RECORDER_STATUS,
                "ffmpeg": FFMPEG_PATH,
                "ffprobe": FFPROBE_PATH,
                "message": RECORDER_MSG,
            }
        )
        st.markdown("#### Recorder bridge history")
        if BRIDGE_STATE.history:
            st.json(BRIDGE_STATE.history[-5:])
        else:
            st.write("No captures yet.")
        if not st.session_state.get("pending_audio_bytes") and BRIDGE_STATE.history:
            if st.button("Adopt last capture (force)"):
                # Try reconstructing using stored meta + (not stored raw bytes, so only meta adoption)
                last = BRIDGE_STATE.history[-1]
                st.warning("Adopted metadata only (raw bytes not cached). Re-record for full pipeline.")
                st.session_state["pending_audio_meta"] = last


def page_onboarding() -> None:
    """Enhanced onboarding with clear value propositions and step-by-step guidance."""
    
    # Hero section with emotional appeal
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 700; 
                   background: linear-gradient(135deg, #1a365d 0%, #d4af37 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   margin-bottom: 1rem;">
            🎙️ Welcome to VocalBrand Supreme
        </h1>
        <p style="font-size: 1.2rem; color: #64748b; max-width: 700px; margin: 0 auto;">
            Transform your voice into a digital asset. Clone once, generate unlimited professional audio in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick start steps with visual indicators
    st.markdown('<div class="vb-section-title">🚀 Get Started in 4 Simple Steps</div>', unsafe_allow_html=True)
    
    from utils.ui import render_steps
    render_steps(1, 4)  # Show we're on step 1 of 4
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="vb-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎤</div>
            <strong>1. Record Sample</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                30-60 seconds of clear voice in a quiet space
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="vb-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🧬</div>
            <strong>2. Clone Voice</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                AI analyzes your voice patterns & creates a unique voice ID
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="vb-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">✍️</div>
            <strong>3. Write Script</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                Enter any text you want spoken in your voice
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="vb-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎵</div>
            <strong>4. Generate Audio</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                Download professional audio in MP3 or WAV format
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Social proof and trust indicators
    st.markdown('<div class="vb-section-title">💎 Why VocalBrand Supreme?</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        from utils.ui import vb_stat_card
        vb_stat_card("success", "99.9%", "Uptime", "Enterprise-grade reliability")
    
    with col2:
        from utils.ui import vb_stat_card
        vb_stat_card("info", "4", "Premium Voices", "Automatic fallback protection")
    
    with col3:
        from utils.ui import vb_stat_card
        vb_stat_card("brand", "<1.2s", "Average Latency", "Lightning-fast generation")
    
    st.markdown("---")
    
    # Use cases to inspire users
    st.markdown('<div class="vb-section-title">🎯 Perfect For</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Content Creators:**
        - 🎬 YouTube voiceovers
        - 🎙️ Podcast production
        - 📱 Social media content
        - 🎮 Gaming commentary
        
        **Business Professionals:**
        - 📞 IVR & phone systems
        - 📧 Email marketing videos
        - 🎓 Training materials
        - 🔔 Notification systems
        """)
    
    with col2:
        st.markdown("""
        **Agencies & Teams:**
        - 🏢 Client presentations
        - 📊 Demo videos
        - 🌐 Website audio
        - 🎯 Ad campaigns
        
        **Educators & Trainers:**
        - 📚 E-learning courses
        - 🎤 Audiobooks
        - 🧑‍🏫 Lecture recordings
        - 📖 Educational content
        """)
    
    st.markdown("---")
    
    # System metrics in an elegant expander
    with st.expander("📊 System Performance Metrics", expanded=False):
        render_metrics_panel()
    
    # Call to action
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 12px; 
                color: white; 
                text-align: center;
                margin-top: 2rem;">
        <h3 style="margin: 0 0 1rem 0;">Ready to Clone Your Voice? 🚀</h3>
        <p style="margin: 0 0 1rem 0; opacity: 0.95;">
            Head to the <strong>Clone Voice</strong> page to get started, or explore <strong>Generate Speech</strong> to try our demo voices!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick tips section
    st.markdown("---")
    st.markdown("### 💡 Pro Tips for Best Results")
    
    with st.expander("🎤 Recording Quality Tips"):
        st.markdown("""
        **For best voice cloning results:**
        
        ✅ **DO:**
        - Record in a quiet room (no background noise)
        - Speak naturally and clearly
        - Use good quality microphone (built-in is usually fine)
        - Read varied content with different emotions
        - Aim for 60 seconds of audio
        - Maintain consistent volume
        
        ❌ **AVOID:**
        - Recording in noisy environments
        - Speaking too close or too far from mic
        - Monotone reading
        - Audio shorter than 30 seconds
        - Distorted or clipped audio
        - Multiple speakers in the sample
        """)
    
    with st.expander("⚡ Speed & Quality"):
        st.markdown("""
        **Voice Cloning Speed:**
        - Typically completes in 30-45 seconds
        - Processing happens on ElevenLabs servers
        - You'll get a unique voice ID instantly
        
        **Generation Speed:**
        - Most generations: < 2 seconds
        - Average: 1.2 seconds
        - Longer texts may take 3-5 seconds
        - Premium users get priority processing
        """)
    
    with st.expander("💎 Upgrading to Pro"):
        st.markdown("""
        **Free Tier Includes:**
        - 3 test generations to try the system
        - Access to demo voices
        - Basic voice cloning
        
        **Pro Tier Gets You:**
        - ✨ **Unlimited generations**
        - ⚡ Priority processing queue
        - 💼 Commercial license
        - 🎛️ Advanced voice controls
        - 🛟 24/7 premium support
        - 🎯 No rate limits
        
        **Pricing:**
        - Monthly: €29/month (cancel anytime)
        - Annual: €290/year (save 17% - 2 months free!)
        
        👉 Check the sidebar for upgrade options
        """)



def page_clone() -> None:
    render_clone_section()


def page_generate() -> None:
    render_generation_section()
    if st.session_state.get("tts_history"):
        with st.expander("Generation history", expanded=False):
            st.json(st.session_state["tts_history"][::-1][:10])


def page_admin() -> None:
    st.subheader("Admin dashboard")
    st.write("Recent clones")
    st.json(st.session_state.get("clone_history", [])[-10:])
    st.write("Recorder hits", BRIDGE_STATE.hits)
    st.write("Latest bridge payload")
    st.json(BRIDGE_STATE.snapshot())


def page_contact() -> None:
    """Contact form page with enhanced UX."""
    st.title("📧 Contact Us")
    
    # Professional hero section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 12px; 
                color: white; 
                margin-bottom: 2rem;
                text-align: center;">
        <h3 style="margin: 0 0 0.5rem 0;">We're Here to Help! 🚀</h3>
        <p style="margin: 0; opacity: 0.95;">
            Have questions about pricing, features, or need technical support? 
            Our team typically responds within 24 hours.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if email is configured
    if not is_email_configured():
        st.warning("""
        ⚠️ **Contact form is currently being configured.** 
        
        In the meantime, you can reach us through:
        - Our support portal (check your account dashboard)
        - The in-app chat feature
        - Your account manager if you're on a premium plan
        """)
        return
    
    # Contact form with better visual hierarchy
    with st.form("contact_form", clear_on_submit=True):
        st.markdown("### Send us a message")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Your Name *", 
                placeholder="Jane Smith",
                help="How should we address you?"
            )
        
        with col2:
            email = st.text_input(
                "Your Email *", 
                placeholder="jane@company.com",
                help="We'll reply to this address"
            )
        
        # Subject dropdown for better categorization
        subject_options = [
            "General Question",
            "Pricing & Billing",
            "Technical Support",
            "Feature Request",
            "Bug Report",
            "Partnership Inquiry",
            "Other"
        ]
        subject_type = st.selectbox(
            "Subject Category *",
            subject_options,
            help="Help us route your message to the right team"
        )
        
        subject_detail = st.text_input(
            "Subject Details *",
            placeholder="Brief description of your inquiry...",
            help="A short summary helps us respond faster"
        )
        
        message = st.text_area(
            "Your Message *",
            placeholder="Please provide as much detail as possible. For technical issues, include:\n• What you were trying to do\n• What happened instead\n• Any error messages you saw",
            height=200,
            help="The more details you provide, the better we can help"
        )
        
        # Combine subject for email
        full_subject = f"[{subject_type}] {subject_detail}" if subject_detail else subject_type
        
        # Submit button with enhanced styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "📨 Send Message", 
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            # Validate inputs with helpful error messages
            errors = []
            if not name or len(name.strip()) < 2:
                errors.append("Please enter your full name (at least 2 characters)")
            if not email or "@" not in email or "." not in email.split("@")[-1]:
                errors.append("Please enter a valid email address")
            if not subject_detail or len(subject_detail.strip()) < 3:
                errors.append("Please provide a subject (at least 3 characters)")
            if not message or len(message.strip()) < 10:
                errors.append("Please provide a detailed message (at least 10 characters)")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Send email with loading state
                with st.spinner("✨ Sending your message..."):
                    success, result_msg = send_contact_email(
                        name.strip(), 
                        email.strip(), 
                        full_subject, 
                        message.strip()
                    )
                
                if success:
                    st.success(f"""
                    ✅ **Message sent successfully!**
                    
                    {result_msg}
                    
                    📬 You should receive a confirmation email shortly at **{email}**
                    """)
                    st.balloons()
                else:
                    st.error(f"""
                    ❌ **Oops! Something went wrong.**
                    
                    {result_msg}
                    
                    💡 **What to do next:**
                    - Check your internet connection
                    - Try again in a few minutes
                    - If the problem persists, check your account dashboard for alternative contact methods
                    """)
    
    # Info section with visual cards
    st.markdown("---")
    st.markdown("### 💡 What to expect")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="vb-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
            <strong>Fast Response</strong>
            <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
                Usually within 24 hours
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="vb-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💎</div>
            <strong>Priority for Pro</strong>
            <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
                Premium members get priority support
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="vb-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
            <strong>Expert Help</strong>
            <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
                Our team knows VocalBrand inside out
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Common questions quick links
    st.markdown("---")
    st.markdown("### 🔍 Common Questions")
    
    with st.expander("💰 Pricing & Plans"):
        st.markdown("""
        **Monthly Pro (€29/mo):**
        - Unlimited voice generations
        - Priority processing
        - Commercial license
        - Cancel anytime
        
        **Annual Pro (€290/yr):**
        - Everything in Monthly
        - Save 17% (2 months free)
        - Best value for committed users
        
        👉 Visit the Onboarding page to see all payment options
        """)
    
    with st.expander("🎤 Voice Cloning Questions"):
        st.markdown("""
        **How long should my voice sample be?**
        - Minimum: 30 seconds
        - Recommended: 60 seconds
        - Best quality: Clean, clear audio in a quiet environment
        
        **What formats are supported?**
        - Record directly in the browser (recommended)
        - Upload WAV, MP3, or M4A files
        
        **Can I clone multiple voices?**
        - Yes! Each clone gets a unique voice ID
        - Store unlimited voices in your account
        """)
    
    with st.expander("🔧 Technical Support"):
        st.markdown("""
        **For fastest support, include:**
        - What you were trying to do
        - What happened instead
        - Screenshots of any error messages
        - Your browser and operating system
        
        **Common fixes:**
        - Try refreshing the page
        - Check your subscription status
        - Ensure your browser has microphone permissions
        - Clear your browser cache
        """)
    
    with st.expander("💳 Billing Questions"):
        st.markdown("""
        **Subscription Management:**
        - Monthly subscriptions can be cancelled anytime in Stripe
        - Annual subscriptions provide 17% savings
        - All payments are processed securely via Stripe
        
        **Refund Policy:**
        - Contact us within 7 days for refund requests
        - We're happy to work with you on any billing issues
        
        **Need an invoice?**
        - Available for all Pro subscribers
        - Request through this contact form
        """)



def main() -> None:
    configure_page()
    init_db()
    ensure_demo_user()
    ensure_session_defaults()
    ensure_voice_reset_on_logout()
    inject_css()
    # Inject SEO meta tags for search engine optimization
    try:
        inject_seo_meta()
    except Exception:
        pass
    # If auth failed to import, stop early with a clear diagnostic
    if AUTH_IMPORT_ERROR is not None:
        st.error(
            "Authentication module failed to import. This usually means a conflicting 'auth' package, missing passlib, or stale __pycache__.\n\n"
            f"Root cause: {AUTH_IMPORT_ERROR}\n\n"
            "Troubleshooting:\n"
            "1) Ensure you're launching Streamlit from the project folder containing 'auth.py'.\n"
            "2) Delete any __pycache__ folders.\n"
            "3) Check that no folder or file elsewhere is named 'auth' shadowing this module.\n"
            "4) Install required deps: passlib[bcrypt].\n\n"
            "After fixing, restart the app."
        )
        return
    # Add visual-only, mobile-friendly sidebar opener
    try:
        inject_mobile_nav_helpers()
    except Exception:
        pass
    # Brand the sidebar with logo if available
    try:
        if Path("logo.png").exists():
            st.sidebar.image("logo.png", width="stretch")
            st.sidebar.markdown("---")
    except Exception:
        pass
    # If coming back from Stripe, finalize subscription before rendering panels
    handle_billing_return()
    render_account_panel()

    if not st.session_state.get("user_id"):
        login_section()
        return

    st.title("🎙️ VocalBrand Supreme Console")
    nav_options = ["Onboarding", "Clone Voice", "Generate Speech", "Contact"]
    if st.session_state.get("user_is_admin"):
        nav_options.append("Admin")
    current_page = st.sidebar.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state.get("nav_page", "Onboarding")),
    )
    st.session_state["nav_page"] = current_page

    if current_page == "Onboarding":
        page_onboarding()
    elif current_page == "Clone Voice":
        page_clone()
    elif current_page == "Generate Speech":
        page_generate()
    elif current_page == "Contact":
        page_contact()
    elif current_page == "Admin":
        page_admin()


if __name__ == "__main__":
    main()
