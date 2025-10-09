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
from engine import DEFAULT_MODEL_ID, DEFAULT_OUTPUT_FORMAT, VocalBrandEngine
from payment import PaymentManager
from utils.audio_utils import validate_audio_bytes, quality_score
from utils.ffmpeg_auto import attempt_auto_ffmpeg
from utils.ui import inject_css, inject_mobile_nav_helpers

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
    if billing == "success" and sess_id and payment_manager and st.session_state.get("user_id"):
        sub_id = payment_manager.get_subscription_id_from_session(str(sess_id))
        if sub_id:
            # Persist to DB and session
            try:
                from auth import set_subscription

                set_subscription(st.session_state["user_id"], True, stripe_sub_id=sub_id)
                st.session_state["subscription_active"] = True
                st.success("Subscription activated! 🎉")
            except Exception:
                st.session_state["subscription_active"] = True
        # Clean query params (refresh without them)
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
engine = VocalBrandEngine(ELEVENLABS_KEY)
if engine.offline:
    logger.warning("Engine operating in offline mode (%s)", engine.offline_reason)

STRIPE_KEY = get_secret("STRIPE_API_KEY", os.getenv("STRIPE_API_KEY", "")) or ""
STRIPE_PRICE_ID = get_secret("STRIPE_PRICE_ID")
payment_manager = PaymentManager(STRIPE_KEY, price_id=STRIPE_PRICE_ID) if STRIPE_KEY else None

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
    "use_pro_recorder": False,  # Force built-in HTML5 recorder even if native present (gives live timer+waveform)
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
            page_title="VocalBrand - Enterprise Voice Cloning",
            page_icon=page_icon,
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                "Get Help": "https://vocalbrand.com/support",
                "Report a bug": "https://vocalbrand.com/bug",
                "About": "VocalBrand - World's Most Robust Voice Cloning SaaS",
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
            <div style="display:flex;gap:0.5rem;align-items:center;flex-wrap:wrap;">
                <button id="vb_start" style="padding:0.5rem 1rem;">🎙️ Start</button>
                <button id="vb_stop" style="padding:0.5rem 1rem;" disabled>⏹️ Stop</button>
                <span id="vb_status" style="font-size:0.85rem;color:#555;">Idle</span>
                <span id="vb_level" style="font-size:0.75rem;color:#666;">Level: -- dB | 0.0s</span>
            </div>
            <canvas id="vb_canvas" width="600" height="64" style="margin-top:4px;width:100%;height:64px;background:#111;border-radius:4px;"></canvas>
            <audio id="vb_play" controls style="margin-top:0.5rem;width:100%;display:none;"></audio>
            <div id="vb_download_wrap" style="margin-top:0.25rem;display:none;"><a id="vb_download" download="vocalbrand_recording.webm">Download recording</a></div>
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
            ctx.fillStyle = '#111'; ctx.fillRect(0,0,W,H);
            ctx.strokeStyle = '#2ee'; ctx.lineWidth = 2; ctx.beginPath();
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
                mediaRecorder = new MediaRecorder(stream);
                chunks=[]; mediaRecorder.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data); };
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
        st.checkbox("Use Pro Recorder (timer + waveform)", key="use_pro_recorder")
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
            if result.get("success"):
                st.session_state["clone_voice_id"] = result.get("voice_id", "")
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
                st.success(f"Voice ready! ID: {result.get('voice_id')}")
            else:
                st.error(result.get("message", "Voice cloning failed"))
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
        if result.get("success"):
            st.session_state["clone_voice_id"] = result.get("voice_id", "")
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
    if not voice_id:
        st.warning("Clone a voice before generating audio.")
        return
    st.caption(f"Voice ID: {voice_id}")
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
    container.markdown("### Upgrade to VocalBrand Pro")
    container.markdown(
        """
        **Pro Features:**
        - Unlimited voice generations
        - Priority processing
        - Commercial license
        - Advanced voice controls
        - 24/7 premium support
        """
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
    container.markdown("#### 💎 Subscription Plans")
    
    user_ref = f"user_{st.session_state['user_id']}"
    
    # Monthly subscription (existing in-app flow)
    col1, col2 = container.columns([3, 1])
    with col1:
        container.markdown("**Monthly Pro** — Unlimited generations, cancel anytime")
    with col2:
        if container.button("€29/mo →", key="upgrade_btn_monthly", use_container_width=True):
            url, checkout_id = payment_manager.create_checkout_session(user_ref)
            st.session_state["latest_checkout_id"] = checkout_id
            container.markdown(f"[Open secure checkout]({url})", unsafe_allow_html=True)
    
    # Annual subscription via Payment Link (if configured)
    annual_link = os.getenv("ANNUAL_PAYMENT_LINK")
    if annual_link:
        col1, col2 = container.columns([3, 1])
        with col1:
            container.markdown("**Annual Pro** — Save 17% (€290/year vs €348/year)")
        with col2:
            container.markdown(f"[€290/yr →]({annual_link})", unsafe_allow_html=True)
    
    # One-time professional services
    setup_links = {
        "Setup — Professional": os.getenv("SETUP_PRO_PAYMENT_LINK"),
        "Setup — Enterprise": os.getenv("SETUP_ENT_PAYMENT_LINK"),
    }
    visible_setups = [(label, url) for label, url in setup_links.items() if url]
    
    if visible_setups:
        container.markdown("---")
        container.markdown("#### 🚀 Professional Onboarding")
        container.caption("One-time guided setup services for teams and enterprises")
        
        for label, url in visible_setups:
            price = "€497" if "Professional" in label else "€997"
            col1, col2 = container.columns([3, 1])
            with col1:
                duration = "60 min" if "Professional" in label else "120 min"
                container.markdown(f"**{label}** — {duration} guided setup & Q&A")
            with col2:
                container.markdown(f"[{price} →]({url})", unsafe_allow_html=True)
    
    # Minutes packs for additional usage
    pack_links = {
        "60 min": os.getenv("PACK60_PAYMENT_LINK"),
        "300 min": os.getenv("PACK300_PAYMENT_LINK"),
        "1000 min": os.getenv("PACK1000_PAYMENT_LINK"),
    }
    visible_packs = [(label, url) for label, url in pack_links.items() if url]
    
    if visible_packs:
        container.markdown("---")
        container.markdown("#### ⚡ Additional Minutes Packs")
        container.caption("Premium voice minutes for professional use cases")
        
        pack_prices = {"60 min": "€89", "300 min": "€399", "1000 min": "€1,299"}
        for label, url in visible_packs:
            price = pack_prices.get(label, "See pricing")
            col1, col2 = container.columns([3, 1])
            with col1:
                container.markdown(f"**Voice Minutes Pack {label}**")
            with col2:
                container.markdown(f"[{price} →]({url})", unsafe_allow_html=True)
    
    # Help section
    if visible_setups or visible_packs or annual_link:
        container.markdown("---")
        support_email = os.getenv("SUPPORT_EMAIL", "support@vocalbrand.app")
        
        # Critical: explain automatic activation
        container.info(
            "💡 **Automatic Activation:** Use the same email address for Payment Link checkouts as your VocalBrand account. "
            "Credits are added instantly after payment."
        )
        
        with container.expander("💡 Payment Options FAQ", expanded=False):
            container.markdown(
                f"""
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
                - For account crediting or custom enterprise pricing, contact {support_email}
                
                **How do I switch between Monthly and Annual?**
                - Cancel your Monthly subscription in Stripe, then purchase Annual via the Payment Link above.
                - Or contact {support_email} for assistance with the switch.
                """
            )
    
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
            submitted = st.form_submit_button("Sign in")
            if submitted:
                ok, uid = authenticate(email, password)
                if ok and uid:
                    user = get_user(uid)
                    if user:
                        st.session_state["user_id"] = user["id"]
                        st.session_state["user_email"] = user["email"]
                        st.session_state["subscription_active"] = bool(user.get("subscription_active"))
                        st.success("Signed in successfully.")
                        safe_rerun(0.05)
                        return
                st.error("Invalid credentials. Please try again.")
    with tabs[1]:
        with st.form("register_form"):
            email = st.text_input("Work email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            submitted = st.form_submit_button("Create account")
            if submitted:
                ok, message = register_user(email, password)
                if ok:
                    st.success("Account created. Sign in using your credentials.")
                else:
                    st.warning(f"Registration failed: {message}")


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
    st.subheader("Onboarding")
    st.markdown(
        """
        1. Prepare a quiet 30-60 second voice sample.
        2. Record directly in the browser or upload a WAV/MP3 file.
        3. Clone the voice to get a reusable voice ID.
        4. Generate speech with your custom voice.
        """
    )
    st.markdown("---")
    st.markdown("### Why VocalBrand Supreme?")
    cols = st.columns(3)
    cols[0].metric("Uptime", "99.9%", "enterprise-grade")
    cols[1].metric("Fallback voices", "4 premium")
    cols[2].metric("Latency", "< 1.2s", "average")
    st.markdown("---")
    render_metrics_panel()


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


def main() -> None:
    configure_page()
    init_db()
    ensure_demo_user()
    ensure_session_defaults()
    ensure_voice_reset_on_logout()
    inject_css()
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
    nav_options = ["Onboarding", "Clone Voice", "Generate Speech"]
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
    elif current_page == "Admin":
        page_admin()


if __name__ == "__main__":
    main()
