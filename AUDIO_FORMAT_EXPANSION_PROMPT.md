# 🎧 Audio Format Expansion Prompt (Drop‑in, Safe Across the App)

Use this prompt as a repeatable instruction to expand/standardize supported audio formats in any Streamlit app without breaking existing flows.

---

## Objective
- Allow additional audio formats in drag‑and‑drop uploaders.
- Keep processing/validation paths unchanged (continue to work with bytes/WAV internally).
- Present clear, consistent UI messaging for supported formats.
- Avoid regressions by centralizing configuration and reusing it everywhere.

## Contract
- Input: UploadedFile or raw bytes from any of the supported formats.
- Output: Raw WAV bytes stored in session (if needed), plus metadata.
- Error Modes: Unsupported format, decode failure (ffmpeg), oversize file.
- Success Criteria: Upload accepts files; app validates and proceeds to clone.

## Steps (Apply These Edits)

1) Introduce centralized constants and helpers near imports:

```python
ACCEPTED_AUDIO_EXTS: list[str] = [
    "wav", "mp3", "m4a", "aac", "ogg", "flac", "aiff", "webm"
]

def accepted_formats_display() -> str:
    return ", ".join(ext.upper() for ext in ACCEPTED_AUDIO_EXTS)
```

2) Update every `st.file_uploader` call to use the same source of truth:

```python
uploaded = st.file_uploader(
    f"Upload Audio ({accepted_formats_display()})",
    type=ACCEPTED_AUDIO_EXTS,
    key="<unique_key>",
    label_visibility="visible"
)
st.caption(f"Supported: {accepted_formats_display()} • Max 200 MB • Drag & drop or click Browse")
```

3) Ensure ingestion converts to a normalized format (WAV) when needed:

- For browser recordings (webm/mp4/aac), decode with pydub/ffmpeg and export to WAV.
- For uploaded files, `AudioSegment.from_file(BytesIO(data))` is typically sufficient (ffmpeg required).

Example (already present in this app for Pro Recorder):
```python
from pydub import AudioSegment
seg = AudioSegment.from_file(BytesIO(raw_blob), format=fmt)
wav_buf = BytesIO()
seg.export(wav_buf, format="wav")
wav_bytes = wav_buf.getvalue()
```

4) Keep session state flow intact:
- Store bytes in `st.session_state["audio_data"]` and set `flow_state` to the next step.
- When needed, set `show_guidance_message=True` and `scroll_to_upload=True` then `st.rerun()`.

5) Test matrix (happy + edge):
- MP3, M4A, AAC, OGG, FLAC, AIFF, WEBM, WAV
- Large file near the limit
- Corrupt/zero-byte file
- iOS Safari recording (mp4/aac) -> confirm decode via ffmpeg

---

## Notes
- ffmpeg must be available; see repo docs for install.
- Pydub delegates decoding to ffmpeg; unsupported formats will raise and should surface a helpful error.
- Use the constant everywhere to avoid drift in accepted types.

---

## Done-For-You Implementation
This repository already includes the centralized constants and updated upload widgets. To add new formats later, update `ACCEPTED_AUDIO_EXTS` and the UI will reflect the change automatically.
