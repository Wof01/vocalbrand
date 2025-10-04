import os, sys
from io import BytesIO
import base64
import pytest

# Ensure project root on path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.audio_utils import validate_audio_bytes, quality_score  # type: ignore

# Simple 1kHz sine wave generator (fallback) without external libs if pydub not available.

def _generate_sine_wav(duration_sec=6.0, sample_rate=16000):
    import math, struct
    n_samples = int(duration_sec * sample_rate)
    buf = BytesIO()
    # Write minimal WAV header later; collect frames first
    frames = BytesIO()
    freq = 440.0
    for i in range(n_samples):
        val = int(32767 * 0.2 * math.sin(2*math.pi*freq * (i / sample_rate)))
        frames.write(struct.pack('<h', val))
    data = frames.getvalue()
    # WAV header
    riff_size = 36 + len(data)
    header = b'RIFF' + (riff_size).to_bytes(4,'little') + b'WAVEfmt ' + (16).to_bytes(4,'little') + (1).to_bytes(2,'little') + (1).to_bytes(2,'little') + (sample_rate).to_bytes(4,'little') + (sample_rate*2).to_bytes(4,'little') + (2).to_bytes(2,'little') + (16).to_bytes(2,'little') + b'data' + len(data).to_bytes(4,'little')
    return header + data

def test_validate_too_short():
    tiny = b'\x00' * 1000
    res = validate_audio_bytes(tiny)
    assert res['ok'] is False
    assert 'short' in res['message'].lower()

def test_validate_good_sample():
    wav = _generate_sine_wav(6.0)
    res = validate_audio_bytes(wav)
    # May decode or fallback; accept ok True
    assert res['ok'] is True
    # Duration either measured or 0 if unparsed
    assert 'message' in res

@pytest.mark.parametrize('dur, loud, expected', [
    (30, -14, 'Good'),   # ideal duration + good loudness
    (20, -20, 'Fair'),   # mid duration bucket + mid loudness bucket
    (10, -14, 'Fair'),   # short duration (no duration points) but good loudness -> 60 => Fair
])
def test_quality_score(dur, loud, expected):
    out = quality_score(dur, loud)
    assert out['label'] == expected
