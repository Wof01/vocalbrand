"""VocalBrand Engine - resilient ElevenLabs integration with fallbacks."""
from __future__ import annotations
import time
import os
import requests
from io import BytesIO
from typing import Optional, Dict, Any, Tuple
from metrics import metrics_collector
import logging

logger = logging.getLogger("vocalbrand.engine")

ELEVEN_VOICE_ADD_URL = "https://api.elevenlabs.io/v1/voices/add"
ELEVEN_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
DEFAULT_MODEL_ID = "eleven_monolingual_v1"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"

class VocalBrandEngine:
    def __init__(self, api_key: str, *, timeout: int = 40, retries: int = 3, voice_manager=None):
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.voice_manager = voice_manager  # Optional VoiceManager for quota handling
        # Updated fallback voices - using current ElevenLabs pre-built voice IDs
        # These are stable voice IDs that exist in all ElevenLabs accounts
        self.fallback_voices = [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel (v2 - updated ID)
            "AZnzlk1XvdvUeBnXmlld",  # Domi
            "EXAVITQu4vr4xnSDxMaL",  # Bella
            "ErXwobaYiN019PkySvjV",  # Antoni
        ]
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
        """Clone a voice from audio sample.
        
        Returns:
            Dict with keys:
                - success: True if successfully cloned with ElevenLabs, False if fallback used
                - voice_id: The voice ID (real if success=True, fallback if success=False)
                - provider: Source of the voice (elevenlabs_primary, fallback_prebuilt, etc.)
                - message: Human-readable status message
                - error_detail: Optional detailed error information
        """
        if self.offline:
            # Offline: simulate cloning instantly
            return {
                "success": False,
                "voice_id": self._fallback_voice(),
                "provider": "offline_sim",
                "message": "Offline mode: cannot clone voice",
                "error_detail": "API key not configured or offline mode enabled"
            }
        
        attempts = 0
        last_error: Optional[Exception] = None
        last_response_text = ""
        
        while attempts < self.retries:
            try:
                raw_bytes = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file.read()
                
                # Validate audio data
                if not raw_bytes or len(raw_bytes) < 4000:  # ~4 KB sanity (very short / invalid)
                    return {
                        "success": False,
                        "voice_id": None,
                        "provider": "input_rejected",
                        "message": "Audio sample too short or unreadable (minimum 4KB required)",
                        "error_detail": f"Audio size: {len(raw_bytes) if raw_bytes else 0} bytes"
                    }
                
                # Attempt to clone with ElevenLabs
                files = {"files": (audio_file.name, raw_bytes)}
                data = {"name": voice_name}
                resp = requests.post(
                    ELEVEN_VOICE_ADD_URL,
                    headers=self._headers(),
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
                
                last_response_text = resp.text[:500]  # Save for error reporting
                
                if resp.status_code == 200:
                    j = resp.json()
                    vid = j.get("voice_id") or j.get("voice", {}).get("voice_id")
                    if vid:
                        return {
                            "success": True,
                            "voice_id": vid,
                            "provider": "elevenlabs_primary",
                            "message": f"Voice '{voice_name}' cloned successfully!"
                        }
                
                # Non-200 response
                if 400 <= resp.status_code < 500:
                    # Client error - don't retry
                    error_msg = f"ElevenLabs API error (status {resp.status_code})"
                    error_data = None
                    
                    try:
                        error_data = resp.json()
                        error_msg = error_data.get("detail") or error_data.get("message") or error_msg
                    except:
                        pass
                    
                    # CRITICAL: Handle voice limit reached error
                    if error_data and isinstance(error_data, dict):
                        status = error_data.get("status", "")
                        
                        if status == "voice_limit_reached":
                            # Voice quota full - attempt auto-cleanup
                            logger.warning(f"Voice limit reached, attempting auto-cleanup...")
                            
                            if self.voice_manager:
                                cleanup_result = self.voice_manager.auto_cleanup_if_needed(keep_count=25)
                                
                                if cleanup_result.get("cleaned"):
                                    # Cleanup successful, retry cloning once
                                    logger.info(f"Cleanup successful, retrying voice clone...")
                                    
                                    # Retry the clone request once
                                    try:
                                        retry_resp = requests.post(
                                            ELEVEN_VOICE_ADD_URL,
                                            headers=self._headers(),
                                            files=files,
                                            data=data,
                                            timeout=self.timeout
                                        )
                                        
                                        if retry_resp.status_code == 200:
                                            j = retry_resp.json()
                                            vid = j.get("voice_id") or j.get("voice", {}).get("voice_id")
                                            if vid:
                                                return {
                                                    "success": True,
                                                    "voice_id": vid,
                                                    "provider": "elevenlabs_after_cleanup",
                                                    "message": f"Voice '{voice_name}' cloned successfully (after auto-cleanup)!",
                                                    "cleanup_performed": True
                                                }
                                    except Exception as retry_err:
                                        logger.error(f"Retry after cleanup failed: {retry_err}")
                            
                            # Cleanup failed or didn't help
                            return {
                                "success": False,
                                "voice_id": None,
                                "provider": "quota_exceeded",
                                "message": "Voice quota limit reached",
                                "error_detail": str(error_data),
                                "actionable_message": (
                                    "Your ElevenLabs account has reached the maximum voice limit (30 voices). "
                                    "Please delete some old voices from your ElevenLabs dashboard, or upgrade your plan."
                                )
                            }
                    
                    return {
                        "success": False,
                        "voice_id": None,
                        "provider": "api_error",
                        "message": f"Voice cloning failed: {error_msg}",
                        "error_detail": last_response_text
                    }
                
            except requests.Timeout:
                last_error = Exception(f"Request timeout after {self.timeout}s")
            except Exception as e:
                last_error = e
            
            attempts += 1
            if attempts < self.retries:
                time.sleep(min(2 ** attempts, 8))
        
        # All retries exhausted
        return {
            "success": False,
            "voice_id": None,
            "provider": "retries_exhausted",
            "message": f"Voice cloning failed after {self.retries} attempts",
            "error_detail": str(last_error) if last_error else last_response_text
        }

    @metrics_collector.timing("tts")
    def text_to_speech(self, text: str, voice_id: str, *, model_id: str | None = None, output_format: str | None = None) -> Tuple[bool, Optional[BytesIO], str]:
        """Generate speech from text using a voice ID.
        
        Returns:
            Tuple of (success, audio_buffer, status_message)
        """
        if self.offline:
            return True, self.emergency_sample(), f"offline-simulated:{self.offline_reason}"
        
        # CRITICAL: Validate voice_id before making API call
        if not voice_id or len(voice_id) < 15:
            return False, None, f"invalid_voice_id:{voice_id}"
        
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
                    detail = j.get('detail', {})
                    if isinstance(detail, dict):
                        error_type = detail.get('status') or detail.get('message') or str(detail)
                    else:
                        error_type = str(detail)
                    
                    msg = j.get('message') or j.get('error') or error_type or body_snip
                    
                    # CRITICAL: Provide actionable error messages
                    if "voice_not_found" in str(msg).lower() or resp.status_code == 404:
                        return False, None, f"{err_tag} api_error: Voice ID not found in ElevenLabs account. Please re-clone your voice."
                    
                    return False, None, f"{err_tag} api_error: {msg}"[:300]
                except Exception:
                    pass
            return False, None, f"{err_tag} body={body_snip}"[:420]
        except Exception as e:  # noqa: BLE001
            return False, None, f"exception:{str(e)}"

    def _fallback_voice(self) -> str:
        return self.fallback_voices[0]

    def emergency_sample(self) -> BytesIO:
        # Very small silent placeholder or beep (placeholder bytes)
        return BytesIO(b"RIFF....VocalBrandFallback")
