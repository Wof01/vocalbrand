"""VocalBrand Engine - resilient ElevenLabs integration with fallbacks."""
from __future__ import annotations
import time
import os
import requests
from io import BytesIO
from typing import Optional, Dict, Any, Tuple
from metrics import metrics_collector

ELEVEN_VOICE_ADD_URL = "https://api.elevenlabs.io/v1/voices/add"
ELEVEN_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
DEFAULT_MODEL_ID = "eleven_monolingual_v1"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"

class VocalBrandEngine:
    def __init__(self, api_key: str, *, timeout: int = 40, retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.fallback_voices = ["Rachel", "Domi", "Bella", "Antoni"]
        # Accept both legacy 'eleven_' and newer 'sk_' secret key formats
        key_pattern_ok = api_key.startswith("eleven_") or api_key.startswith("sk_") if api_key else False
        offline_env_raw = os.getenv("VOCALBRAND_OFFLINE")
        offline_env = False
        if offline_env_raw is not None:
            offline_env = str(offline_env_raw).strip().lower() in {"1", "true", "yes", "on"}
        self.offline = offline_env or not api_key or not key_pattern_ok
        self.offline_reason = None
        if not api_key:
            self.offline_reason = "no_api_key"
        elif not key_pattern_ok:
            self.offline_reason = "unrecognized_key_pattern"
        elif offline_env:
            self.offline_reason = "forced_offline_env"

    def _headers(self) -> Dict[str, str]:
        return {"xi-api-key": self.api_key}

    @metrics_collector.timing("clone_voice")
    def clone_voice(self, audio_file, voice_name: str) -> Dict[str, Any]:
        if self.offline:
            # Offline: simulate cloning instantly
            return {"success": True, "voice_id": self._fallback_voice(), "provider": "offline_sim", "message": "Offline simulated clone"}
        attempts = 0
        last_error: Optional[Exception] = None
        while attempts < self.retries:
            try:
                raw_bytes = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file.read()
                if not raw_bytes or len(raw_bytes) < 4000:  # ~4 KB sanity (very short / invalid)
                    return {"success": False, "voice_id": self._fallback_voice(), "provider": "input_rejected", "message": "Audio sample too short or unreadable"}
                files = {"files": (audio_file.name, raw_bytes)}
                data = {"name": voice_name}
                resp = requests.post(ELEVEN_VOICE_ADD_URL, headers=self._headers(), files=files, data=data, timeout=self.timeout)
                if resp.status_code == 200:
                    j = resp.json()
                    vid = j.get("voice_id") or j.get("voice", {}).get("voice_id")
                    if vid:
                        return {"success": True, "voice_id": vid, "provider": "elevenlabs_primary", "message": "Voice cloned"}
                # treat non-200 as retryable except 4xx
                if 400 <= resp.status_code < 500:
                    break
            except Exception as e:  # noqa: BLE001
                last_error = e
            attempts += 1
            time.sleep(min(2 ** attempts, 8))
        # fallback voice
        return {"success": True, "voice_id": self._fallback_voice(), "provider": "fallback_prebuilt", "message": f"Using fallback voice (error={last_error})"}

    @metrics_collector.timing("tts")
    def text_to_speech(self, text: str, voice_id: str, *, model_id: str | None = None, output_format: str | None = None) -> Tuple[bool, Optional[BytesIO], str]:
        if self.offline:
            return True, self.emergency_sample(), f"offline-simulated:{self.offline_reason}"
        payload = {"text": text, "model_id": model_id or DEFAULT_MODEL_ID}
        if output_format:
            payload["output_format"] = output_format
        try:
            resp = requests.post(
                ELEVEN_TTS_URL.format(voice_id=voice_id),
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
            ctype = resp.headers.get('Content-Type','')
            if resp.status_code == 200:
                # Expect binary (audio/mpeg, audio/*, application/octet-stream)
                if 'json' in ctype.lower():
                    # Unexpected JSON body when success status
                    snippet = resp.text[:300]
                    return False, None, f"json_body_unexpected:{snippet}"
                data = resp.content or b''
                if not data:
                    return False, None, "empty_audio"
                if len(data) < 50:
                    return False, None, f"tiny_audio:{len(data)}"
                # Minimal MP3 header sanity (0xFF 0xFB or 'ID3') optional
                head4 = data[:4]
                if not (head4.startswith(b'ID3') or head4[0] == 0xFF):
                    # Still allow but flag
                    return True, BytesIO(data), f"ok_unusual_header:{head4.hex()}"
                return True, BytesIO(data), "ok"
            # Non-200: attempt parse JSON error
            body_snip = resp.text[:400]
            err_tag = f"status={resp.status_code}"
            if 'application/json' in ctype.lower():
                try:
                    j = resp.json()
                    # surface error fields if present
                    msg = j.get('error') or j.get('detail') or body_snip
                    return False, None, f"{err_tag} api_error:{msg}"[:300]
                except Exception:
                    pass
            return False, None, f"{err_tag} body={body_snip}"[:420]
        except Exception as e:  # noqa: BLE001
            return False, None, str(e)

    def _fallback_voice(self) -> str:
        return self.fallback_voices[0]

    def emergency_sample(self) -> BytesIO:
        # Very small silent placeholder or beep (placeholder bytes)
        return BytesIO(b"RIFF....VocalBrandFallback")
