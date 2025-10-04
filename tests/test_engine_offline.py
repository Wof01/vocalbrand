import os, sys
from io import BytesIO

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine import VocalBrandEngine  # type: ignore

def test_offline_clone_and_tts():
    os.environ['VOCALBRAND_OFFLINE'] = '1'
    engine = VocalBrandEngine(api_key="")
    class Dummy:
        name = "sample.wav"
        def getvalue(self):
            return b"fakeaudio"
    result = engine.clone_voice(Dummy(), "Test Voice")
    assert result['success'] and result['voice_id']
    ok, audio, info = engine.text_to_speech("Hello world", result['voice_id'])
    assert ok and isinstance(audio, BytesIO)
    assert audio.getvalue().startswith(b"RIFF")
