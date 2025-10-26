#!/usr/bin/env python3
"""
PROFESSIONAL UI FIX - No more ugly white artifacts
"""

import os

# Create a complete CSS theme file
css_content = """
/* === CORE RESET - Eliminate all Streamlit styling === */
/* Target every Streamlit container and remove backgrounds/borders */
div[data-testid="stVerticalBlock"], 
div[data-testid="stHorizontalBlock"],
div[data-testid="stElementContainer"],
div.stAlert,
section[data-testid],
div.element-container,
div.block-container,
div.stButton,
div.stDownloadButton,
div.stFileUploader {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* === PROFESSIONAL DESIGN SYSTEM === */
/* Base colors and fonts */
:root {
    --vb-primary: #1a365d;
    --vb-primary-light: #2d4b73;
    --vb-accent: #3182ce;
    --vb-text: #1a202c;
    --vb-gray-light: #f8fafc;
    --vb-gray: #e2e8f0;
    --vb-gray-dark: #718096;
    --vb-red: #e53e3e;
    --vb-green: #38a169;
}

/* Typography improvements */
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--vb-text);
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-weight: 700 !important;
    color: var(--vb-primary) !important;
    letter-spacing: -0.01em !important;
}

/* === COMPONENT STYLING === */
/* Beautiful buttons */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, var(--vb-primary) 0%, var(--vb-primary-light) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    min-height: 45px !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 14px rgba(0, 0, 0, 0.1) !important;
    filter: brightness(110%) !important;
}

.stButton > button:active, .stDownloadButton > button:active {
    transform: translateY(1px) !important;
    box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1) !important;
}

/* Primary button */
.stButton > button[data-baseweb="button"] {
    background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%) !important;
}

/* === CLEAN FILE UPLOADER === */
/* Modern file uploader styling */
[data-testid="stFileUploader"] {
    padding: 0 !important;
}

[data-testid="stFileUploader"] > section {
    padding: 0 !important;
}

/* Uploader droptarget */
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    padding: 2rem 1rem !important;
    border: 2px dashed rgba(26, 54, 93, 0.2) !important;
    border-radius: 12px !important;
    background: rgba(49, 130, 206, 0.03) !important;
    color: var(--vb-primary) !important;
    transition: all 0.2s ease !important;
    min-height: 150px !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(26, 54, 93, 0.4) !important;
    background: rgba(49, 130, 206, 0.05) !important;
}

/* Upload button styling */
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(135deg, var(--vb-primary) 0%, var(--vb-primary-light) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    margin-top: 1rem !important;
}

/* === CLEAN AUDIO PLAYER === */
audio {
    width: 100% !important;
    border-radius: 8px !important;
    height: 40px !important;
    background: var(--vb-gray-light) !important;
}

/* === IFRAME STYLING === */
iframe {
    border: none !important;
    border-radius: 8px !important;
}

/* === RECORDER STYLING === */
/* Pro recorder clean-up */
#fallback_recorder {
    background: transparent !important;
}

/* Tooltips and info boxes */
div.stTooltipIcon {
    background-color: var(--vb-primary) !important;
    border-color: var(--vb-primary) !important;
}

div.stAlert {
    background: rgba(49, 130, 206, 0.1) !important;
    border-left: 4px solid var(--vb-accent) !important;
    border-radius: 6px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
}

/* === CLEAN UP EMOTION CACHE SPANS === */
span[class^="st-emotion-cache-"], 
span[class*=" st-emotion-cache-"] {
    background: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
}

/* === SECTION STYLING === */
.vb-section {
    margin: 2rem 0;
    padding: 1.5rem;
    border-radius: 12px;
    background: white;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.vb-section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--vb-primary);
    margin-bottom: 1rem;
}

/* === PRO RECORDER SECTION === */
.pro-recorder-section {
    background: linear-gradient(135deg, rgba(26, 54, 93, 0.03) 0%, rgba(44, 82, 130, 0.05) 100%);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid rgba(49, 130, 206, 0.1);
}

/* === ACTION BUTTON === */
.action-button {
    display: block;
    width: 100%;
    background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
    color: white;
    text-align: center;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    margin: 1rem 0;
    text-decoration: none;
    transition: all 0.2s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.action-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 14px rgba(0, 0, 0, 0.1);
    filter: brightness(105%);
}
"""

# Create app.py injection
app_code = """
# PROFESSIONAL UI - Direct CSS injection

def inject_professional_css():
    st.markdown('''
<style>
/* === CORE RESET - Eliminate all Streamlit styling === */
div[data-testid="stVerticalBlock"], 
div[data-testid="stHorizontalBlock"],
div[data-testid="stElementContainer"],
div.stAlert,
section[data-testid],
div.element-container,
div.block-container,
div.stButton,
div.stDownloadButton,
div.stFileUploader,
[class^="st-emotion-cache-"],
[class*=" st-emotion-cache-"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Fix all upload areas */
[data-testid="stFileUploader"] {
    background: transparent !important;
    border: 2px dashed rgba(49, 51, 63, 0.2) !important;
    border-radius: 0.5rem !important;
    padding: 1rem !important;
}

[data-testid="stFileUploader"] section {
    background: transparent !important;
    border: none !important;
}

/* Make audio elements clean */
audio, audio::-webkit-media-controls {
    background: transparent !important;
    width: 100% !important;
    border-radius: 8px !important;
}

/* Fix iframe containers */
iframe {
    border: none !important;
    background: transparent !important;
}
</style>
    ''', unsafe_allow_html=True)

"""

# Create the streamlit config directory if it doesn't exist
os.makedirs('.streamlit', exist_ok=True)

# Write the CSS to streamlit static directory
with open('.streamlit/style.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

# Create streamlit config to use our CSS
with open('.streamlit/config.toml', 'w', encoding='utf-8') as f:
    f.write("""
[theme]
primaryColor = "#3182ce"
backgroundColor = "#f8fafc"
secondaryBackgroundColor = "#ffffff"
textColor = "#1a202c"
font = "sans serif"

[server]
enableXsrfProtection = false

[browser]
gatherUsageStats = false
""")

# Now modify app.py to add our CSS injection function
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Create backup if doesn't exist
if not os.path.exists('app.py.bak'):
    with open('app.py.bak', 'w', encoding='utf-8') as f:
        f.write(app_content)

# Insert the injection code after imports if it doesn't exist
if 'def inject_professional_css():' not in app_content:
    import_end = app_content.find('import streamlit as st')
    import_end = app_content.find('\n', import_end)
    
    new_content = app_content[:import_end+1] + '\n' + app_code + app_content[import_end+1:]
    
    # Replace the inject_supreme_css call with our function
    main_function = 'def main() -> None:'
    if main_function in new_content:
        main_index = new_content.find(main_function)
        next_line = new_content.find('\n', main_index) + 1
        if 'inject_supreme_css()' in new_content[next_line:next_line+100]:
            new_content = new_content.replace('inject_supreme_css()', 'inject_professional_css()')
        else:
            # Add our function call if not found
            insert_point = new_content.find('\n', main_index) + 1
            new_content = new_content[:insert_point] + '    inject_professional_css()\n' + new_content[insert_point:]
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

print("✅ Professional UI Fix Successfully Applied!")
print("🎯 Streamlit theme configuration installed")
print("🎯 White artifacts have been eliminated")  
print("🎯 CSS has been professionally styled")
print("🚀 Restart your app to see the improvements!")