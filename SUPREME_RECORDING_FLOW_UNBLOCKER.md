# Supreme Prompt: Recording Flow Unblocker

Objective
- Guarantee recorded audio always advances from Step 1 to Step 2.
- If the browser blocks the “Use This Recording” event or a rerun is missed, show a clear fallback message instructing upload via the dropzone.
- Keep session-state flows consistent and idempotent.

Contract
- Inputs: Any staged audio bytes in `st.session_state` under one or more of: `audio_data`, `pending_audio_bytes`, `pro_recorder_audio_preview`.
- Outputs: `audio_data` set and `flow_state = "processing"`; safe rerun triggered.
- Error modes: Never block UI; on any exception, proceed with normal rendering and show guidance.
- Success criteria: After recording, Step 2 Preview renders automatically; if not, a visible message instructs the user to upload the downloaded file below.

Implementation Steps
1) Safety helper
- Implement `_maybe_force_flow_progression()` that promotes staged bytes to `audio_data`, sets `flow_state = "processing"`, then triggers a rerun.

2) Early call in cloning UI
- Call `_maybe_force_flow_progression()` at the top of `render_clone_section()` after defaults are in place and before Step 1 UI.

3) Pro recorder ingestion parity
- Ensure any pro-recorder capture path calls `_ingest_audio_bytes(...)` and sets `st.session_state["audio_data"]` and `st.session_state["audio_meta"]` so the clone flow has a single source of truth.

4) Fallback user guidance
- Place an info message near the recorder and again near the preview instructing: if auto-progression doesn’t occur, upload the downloaded file in the dropzone below. Keep the accepted formats centralized with `ACCEPTED_AUDIO_EXTS` and show them in the message.

5) Dropzone consistency
- All file uploaders accept: WAV, MP3, M4A, AAC, OGG, FLAC, AIFF, WEBM.
- Display formats via `accepted_formats_display()` to keep the UI consistent.

Validation
- Manual: Record 10–15s, click “Use This Recording”. Expect immediate progression to Step 2; otherwise, see the guidance and successfully continue by uploading the downloaded file.
- Edge cases: Short/quiet audio shows validation warnings but never dead-ends; upload path always available.

Notes
- This prompt is already implemented in `app.py` via `_maybe_force_flow_progression()` and the Step 1/preview info messages.
- The guidance banner can be toggled with `st.session_state["show_guidance_message"]` and optional `scroll_to_upload` to jump to the dropzone anchor.
