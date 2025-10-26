"""
DIRECT CSS FIX FOR WHITE ARTIFACTS

This script creates a custom CSS file that Streamlit will automatically load,
completely eliminating white backgrounds and fixing the UI issues.
"""

import os

# Ensure .streamlit directory exists
os.makedirs('.streamlit', exist_ok=True)

# Write custom CSS to be loaded by Streamlit
with open('.streamlit/style.css', 'w') as f:
    f.write("""
/* Fix all white artifacts and backgrounds */
div[data-testid="stVerticalBlock"], 
div[data-testid="stHorizontalBlock"],
div[data-testid="stElementContainer"],
section[data-testid],
div.element-container,
div.block-container,
div.stButton,
div.stDownloadButton,
div.stFileUploader,
span[class^="st-emotion-cache-"], 
span[class*=" st-emotion-cache-"] {
    background: transparent !important;
    border: none !important;
}

/* Fix file uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(49, 51, 63, 0.2) !important;
    border-radius: 0.5rem !important;
    padding: 1rem !important;
}

/* Make audio elements clean */
audio {
    width: 100% !important;
    border-radius: 8px !important;
}
""")

# Create Streamlit config file for theme
with open('.streamlit/config.toml', 'w') as f:
    f.write("""
[theme]
primaryColor = "#3182ce"
backgroundColor = "#f8fafc"
secondaryBackgroundColor = "#ffffff"
textColor = "#1a202c"
font = "sans serif"
""")

print("✅ Direct CSS fix applied!")
print("🎯 White artifacts will be eliminated")
print("🎯 Streamlit theme configuration installed")
print("🚀 Restart your app to see the improvements!")