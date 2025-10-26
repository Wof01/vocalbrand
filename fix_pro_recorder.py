import re

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the line with pro_val = st.text_area
start_line = None
for i, line in enumerate(lines):
    if 'pro_val = st.text_area' in line:
        start_line = i
        break

if start_line is None:
    print("ERROR: Could not find pro_val line")
    exit(1)

# Find the line with "if pro_val:"
find_line = None
for i in range(start_line, len(lines)):
    if re.match(r'^\s+if pro_val:', lines[i]):
        find_line = i
        break

if find_line is None:
    print("ERROR: Could not find if pro_val: line")
    exit(1)

print(f"Start removal: {start_line}")
print(f"End removal: {find_line}")

# Build replacement (without problematic emojis)
replacement = """        # SUPREME: Direct ingestion when component returns audio
        if pro_component_val and isinstance(pro_component_val, dict) and pro_component_val.get("b64"):
            size = int(pro_component_val.get("size") or 0)
            if size > 1024:
                try:
                    b64 = pro_component_val["b64"]
                    mime = pro_component_val.get("mime", "audio/webm")
                    hk = "pro_h"
                    h = hashlib.sha1(b64.encode()).hexdigest()
                    if st.session_state.get(hk) != h:
                        blob = base64.b64decode(b64)
                        wav = None
                        if len(blob) >= 12 and blob[:4] == b"RIFF" and blob[8:12] == b"WAVE":
                            wav = blob
                        else:
                            try:
                                from pydub import AudioSegment
                                fmt = mime.split("/")[-1].lower() if "/" in mime else "webm"
                                seg = AudioSegment.from_file(BytesIO(blob), format=fmt)
                                buf = BytesIO()
                                seg.export(buf, format="wav")
                                wav = buf.getvalue()
                            except: pass
                        if wav and len(wav) > 100:
                            st.session_state["pro_recorder_audio_preview"] = wav
                            st.session_state[hk] = h
                            meta = _ingest_audio_bytes(wav, source="pro_recorder", filename="recording.wav")
                            _render_audio_feedback(meta, wav)
                            st.success("Recording Locked In", icon="check")
                except Exception as e:
                    st.warning(f"Error: {str(e)[:80]}")
        render_file_upload_fallback()
        return

"""

# Build new lines - keep everything up to and including the st.markdown lines, replace from pro_val through if pro_val:
new_lines = lines[:start_line] + [replacement] + lines[find_line:]

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("SUCCESS: File rewritten")
