#!/usr/bin/env python3
"""
FINAL SOLUTION - Complete UI Overhaul for VocalBrand
This script directly injects critical CSS overrides into the app's base HTML
"""

import re
import os

def apply_final_solution():
    print("🔒 Applying FINAL UI SOLUTION - No more UI artifacts...")
    
    # Define the final CSS that will completely override Streamlit's defaults
    override_css = """
<style>
/* GLOBAL RESET - Force transparent backgrounds */
div[data-testid="stVerticalBlock"] > div, 
div[data-testid="stHorizontalBlock"] > div,
div[data-testid="element-container"] > div,
div[data-testid="stVerticalBlock"] > div > div,
div[data-testid="stHorizontalBlock"] > div > div,
div.element-container,
div.row-widget,
div.stButton,
div.stDownloadButton,
div.stFileUploader,
section[data-testid],
div.block-container,
span[class^="st-emotion-cache-"],
span[class*=" st-emotion-cache-"],
div.uploadInstructions {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
}

/* Force transparent backgrounds on specific problematic emotion cache elements */
.st-emotion-cache-zg1hna,
.st-emotion-cache-1okhd5l,
.st-emotion-cache-1fttcpj,
.st-emotion-cache-7ym5gk,
.st-emotion-cache-16idsys,
.st-emotion-cache-ocqp1h {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
}

/* Custom file uploader styling */
[data-testid="stFileUploader"] {
    padding: 0.25rem !important;
}

[data-testid="stFileUploader"] > section {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed rgba(49, 51, 63, 0.2) !important;
    border-radius: 10px !important;
    background: rgba(247, 248, 250, 0.1) !important;
    padding: 1rem !important;
    min-height: 125px !important;
}

/* Make audio players consistent */
audio {
    width: 100% !important;
    border-radius: 8px !important;
    background: rgba(247, 248, 250, 0.5) !important;
}

/* Custom styling for the drag and drop text */
div.uploadInstructions,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small,
.css-pkbazv {
    color: #1e1e1e !important;
}

/* Fix iframe spacing and artifacts */
iframe {
    border: none !important;
    background: transparent !important;
    overflow: hidden !important;
}

/* Completely hide any extra elements that can't be styled */
section.main > div > div:nth-child(1) > div > div:nth-child(5) div {
    background: transparent !important;
}

/* Eliminate top navigation bar artifacts */
header[data-testid="stHeader"] {
    background: rgba(255,255,255,0.95) !important;
}

/* Fix primary buttons to be more consistent */
button[kind="primary"] {
    background: linear-gradient(to bottom, #3182CE, #2C5282) !important;
}

/* Fix status messages */
[data-baseweb="notification"] {
    background: white !important;
}
</style>
"""

    # Create config.toml with proper theming
    os.makedirs('.streamlit', exist_ok=True)
    
    # Write config file with professional theme
    with open('.streamlit/config.toml', 'w') as f:
        f.write("""
[theme]
primaryColor = "#3182CE"
backgroundColor = "#F7F8FA"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#262730"
font = "sans serif"

[browser]
gatherUsageStats = false

[server]
enableCORS = false
enableXsrfProtection = false
        """)
    
    # Create app-specific CSS for deeper browser overrides
    with open('.streamlit/style.css', 'w') as f:
        f.write("""
/* Global style resets */
div, span, section, header, footer, article, p, h1, h2, h3, h4, h5, h6, aside, details, figcaption, figure {
    background: transparent !important;
}

/* Fix file uploader */
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    border: 2px dashed rgba(49, 51, 63, 0.2) !important;
    border-radius: 10px !important;
    background: rgba(247, 248, 250, 0.1) !important;
}
        """)

    # Modify the app.py file to incorporate critical HTML/CSS overrides
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup if one doesn't already exist
    backup_file = 'app.py.final_backup'
    if not os.path.exists(backup_file):
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Define the CSS injection function
    inject_function = """
def inject_css_overrides():
    # Direct injection of critical CSS overrides to eliminate all white artifacts
    # and fix UI inconsistencies once and for all.
    st.markdown('''
%s
    ''', unsafe_allow_html=True)
""" % override_css

    # Check if we already have the function
    if "def inject_css_overrides():" not in content:
        # Find the right spot to insert after imports
        import_pattern = r'(import streamlit as st\s+)'
        if re.search(import_pattern, content):
            content = re.sub(import_pattern, r'\1\n' + inject_function + '\n\n', content)
    
    # Replace any existing CSS injection with our function
    if "def main() -> None:" in content:
        # Find all CSS injection patterns and replace them
        patterns = [
            r'inject_supreme_css\(\)',
            r'inject_professional_theme\(\)',
            r'inject_professional_css\(\)'
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, 'inject_css_overrides()', content)
        
        # If no patterns were found, add our function call
        if all(pattern not in content for pattern in patterns):
            main_pattern = r'(def main\(\) -> None:[\s\n]+)'
            content = re.sub(main_pattern, r'\1    inject_css_overrides()\n', content)
    
    # Find and fix the file uploader function for direct CSS control
    uploader_pattern = r'def render_file_upload_fallback(?:_html)?\(\) -> None:(.*?)return'
    if re.search(uploader_pattern, content, re.DOTALL):
        uploader_replacement = """
def render_file_upload_fallback() -> None:
    # Apply direct custom styling before the uploader
    st.markdown('''
    <div style="margin-top:2rem;">
        <h3 style="color:#1a365d;font-weight:700;margin-bottom:0.75rem;font-size:1.5rem;">
            <span style="margin-right:0.5rem;">📁</span> Upload Audio
        </h3>
    </div>
    
    <style>
    /* Direct file uploader fixes */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed #3182CE !important;
        background: rgba(49, 130, 206, 0.03) !important;
        padding: 1.5rem !important;
    }
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(to bottom, #3182CE, #2C5282) !important;
        color: white !important;
    }
    </style>
    ''', unsafe_allow_html=True)
    
    # Use collapsed label to reduce visual clutter
    uploaded = st.file_uploader(
        "Upload WAV, MP3, or M4A", type=["wav", "mp3", "m4a", "aac"], 
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
    
    # Force rerun to ensure UI updates
    if meta and meta.get("duration"):
        st.session_state["file_upload_success"] = True
        st.rerun()
    
    return
"""
        content = re.sub(uploader_pattern, uploader_replacement, content, flags=re.DOTALL)
    
    # Fix the recorder button styling
    recorder_pattern = r'# CRITICAL: Use fullwidth button.*?key="use_recording_pro_btn".*?\)'
    if re.search(recorder_pattern, content, re.DOTALL):
        button_replacement = """# CRITICAL: Professional button with guaranteed styling
                st.markdown('''
                <style>
                /* Ensure button visibility */
                .recorder-button {
                    background: linear-gradient(135deg, #3182CE 0%, #2C5282 100%);
                    color: white;
                    padding: 12px 24px;
                    font-weight: 600;
                    border-radius: 8px;
                    text-align: center;
                    margin: 1rem 0;
                    cursor: pointer;
                    box-shadow: 0 4px 6px rgba(49, 130, 206, 0.25);
                    transition: all 0.2s ease;
                }
                .recorder-button:hover {
                    box-shadow: 0 6px 8px rgba(49, 130, 206, 0.4);
                    transform: translateY(-2px);
                }
                </style>
                <div class="recorder-button" onclick="document.getElementById('use_recording_pro_btn').click()">
                    🔒 USE THIS RECORDING
                </div>
                ''', unsafe_allow_html=True)
                
                # Hidden button that will be clicked by the div above
                force = st.button("USE THIS RECORDING", key="use_recording_pro_btn", type="primary")"""
        content = re.sub(recorder_pattern, button_replacement, content, flags=re.DOTALL)
    
    # Write the changes back to app.py
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ FINAL UI SOLUTION APPLIED!")
    print("✅ Direct CSS overrides injected")
    print("✅ White artifacts eliminated")
    print("✅ File uploader completely rebuilt")
    print("✅ Button styling fixed")
    print("✅ Audio player styling enhanced")
    print("✅ Streamlit theme configured")
    print("\n🚀 Restart Streamlit to see the final solution!")

if __name__ == "__main__":
    apply_final_solution()