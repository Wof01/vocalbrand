import os, sys, hashlib
from io import BytesIO

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.audio_utils import validate_audio_bytes  # type: ignore


def _generate_sine_wav(duration_sec=6.0, sample_rate=16000):
    import math, struct
    n_samples = int(duration_sec * sample_rate)
    frames = BytesIO()
    freq = 523.25
    for i in range(n_samples):
        val = int(32767 * 0.15 * math.sin(2*math.pi*freq * (i / sample_rate)))
        frames.write(struct.pack('<h', val))
    data = frames.getvalue()
    riff_size = 36 + len(data)
    header = b'RIFF' + (riff_size).to_bytes(4,'little') + b'WAVEfmt ' + (16).to_bytes(4,'little') + (1).to_bytes(2,'little') + (1).to_bytes(2,'little') + (sample_rate).to_bytes(4,'little') + (sample_rate*2).to_bytes(4,'little') + (2).to_bytes(2,'little') + (16).to_bytes(2,'little') + b'data' + len(data).to_bytes(4,'little')
    return header + data


def test_hash_generation_consistency():
    wav = _generate_sine_wav()
    res = validate_audio_bytes(wav)
    assert res['ok'] is True
    h1 = hashlib.sha1(wav[:50000]).hexdigest()
    h2 = hashlib.sha1(wav[:50000]).hexdigest()
    assert h1 == h2
    assert len(h1) == 40
