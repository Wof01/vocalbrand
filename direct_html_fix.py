"""
DIRECT HTML INJECTION FIX

This script modifies your app.py to use direct HTML instead of Streamlit components
for the problematic upload section.
"""

import re

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup file if needed
if not re.search(r'def render_file_upload_fallback_html', content):
    with open('app.py.backup2', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Created backup: app.py.backup2")

# Create a completely custom HTML version of the uploader
new_func = """
def render_file_upload_fallback_html() -> None:
    """
    A completely custom HTML version of the file uploader that avoids Streamlit's styling issues.
    """
    st.markdown('''
    <style>
    /* Hide any unwanted white backgrounds */
    [data-testid="stFileUploader"], 
    [class^="st-emotion-cache-"], 
    [class*=" st-emotion-cache-"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Custom uploader styling */
    .custom-uploader {
        border: 2px dashed #3182ce;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background-color: rgba(49, 130, 206, 0.05);
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .custom-uploader:hover {
        background-color: rgba(49, 130, 206, 0.1);
        border-color: #2c5282;
    }
    </style>
    
    <div class="custom-uploader">
        <h3 style="margin-top:0;color:#1a365d;font-size:1.5rem;font-weight:bold;">
            📁 Upload Audio
        </h3>
        <p style="color:#4a5568;">
            Provide a high-quality recording for best results
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Keep the actual uploader functionality but make it more minimal
    uploaded = st.file_uploader(
        "Upload WAV, MP3, or M4A file", type=["wav", "mp3", "m4a", "aac"], 
        key="clone_file_upload", label_visibility="collapsed"
    )
    
    if not uploaded:
        return
    raw_bytes = uploaded.read()
    if not raw_bytes:
        st.warning("Uploaded file appears empty.")
        return
    meta = _ingest_audio_bytes(raw_bytes, source="upload", filename=uploaded.name)
    _render_audio_feedback(meta, raw_bytes)
    
    # Inject a bit more styling to clean up any artifacts
    st.markdown('''
    <style>
    audio {
        width: 100% !important;
        border-radius: 8px !important;
    }
    </style>
    ''', unsafe_allow_html=True)
"""

# Find the current function and replace it
pattern = r'def render_file_upload_fallback\(\) -> None:.*?_render_audio_feedback\(meta, raw_bytes\)'
if re.search(pattern, content, re.DOTALL):
    new_content = re.sub(pattern, new_func, content, flags=re.DOTALL)
    
    # Update all calls to use the new function name
    new_content = new_content.replace('render_file_upload_fallback()', 'render_file_upload_fallback_html()')
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("✅ Direct HTML injection fix applied!")
    print("🎯 Created custom HTML uploader")
    print("🎯 Bypassed Streamlit's styling limitations")
    print("🚀 Restart your app to see the improvements!")
else:
    print("❌ Could not find the file uploader function to replace.")
    print("Please check your app.py file structure.")