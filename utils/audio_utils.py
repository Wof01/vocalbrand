"""Audio utility functions for validation, normalization metrics.

Functions:
    validate_audio_bytes(data: bytes) -> dict
        Returns dictionary with keys:
            ok (bool), message (str), duration (float seconds), loudness_dbfs (float or None), raw_bytes (bytes)
"""
from __future__ import annotations
from io import BytesIO
from typing import Dict, Any

MIN_DURATION_SEC = 5.0
MAX_DURATION_SEC = 120.0
MIN_SIZE_BYTES = 15_000  # heuristic pre-parse

def validate_audio_bytes(data: bytes) -> Dict[str, Any]:
    if not data:
        return {"ok": False, "message": "No audio provided", "duration": 0.0, "loudness_dbfs": None, "raw_bytes": data}
    if len(data) < MIN_SIZE_BYTES:
        return {"ok": False, "message": "Audio too short (need >5s of clear speech)", "duration": 0.0, "loudness_dbfs": None, "raw_bytes": data}
    try:
        from pydub import AudioSegment  # type: ignore
        seg = AudioSegment.from_file(BytesIO(data))
        dur = len(seg) / 1000.0
        if dur < MIN_DURATION_SEC:
            return {"ok": False, "message": "Sample under 5 seconds – provide at least 5s", "duration": dur, "loudness_dbfs": seg.dBFS, "raw_bytes": data}
        if dur > MAX_DURATION_SEC:
            return {"ok": False, "message": "Sample over 120 seconds – trim shorter", "duration": dur, "loudness_dbfs": seg.dBFS, "raw_bytes": data}
        return {"ok": True, "message": "ok", "duration": dur, "loudness_dbfs": seg.dBFS, "raw_bytes": data}
    except Exception:
        # fallback heuristic if decode failed
        if len(data) < (2 * MIN_SIZE_BYTES):  # still quite small
            return {"ok": False, "message": "Audio appears invalid or unreadable", "duration": 0.0, "loudness_dbfs": None, "raw_bytes": data}
        return {"ok": True, "message": "ok (unparsed)", "duration": 0.0, "loudness_dbfs": None, "raw_bytes": data}

def quality_score(duration: float, loudness_dbfs: float | None) -> dict:
    score = 0
    if loudness_dbfs is not None:
        if -18 <= loudness_dbfs <= -10:
            score += 60
        elif -24 <= loudness_dbfs < -18 or -10 < loudness_dbfs <= -6:
            score += 35
    if 25 <= duration <= 70:
        score += 40
    elif 15 <= duration < 25 or 70 < duration <= 90:
        score += 20
    label = 'Good' if score >= 80 else 'Fair' if score >= 55 else 'Poor'
    return {"score": score, "label": label}
