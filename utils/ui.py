"""UI helpers for VocalBrand Streamlit app."""
from __future__ import annotations
import streamlit as st
from typing import Iterable

SUPREME_CSS = """
<style>
:root { 
    --primary-blue:#1a365d; 
    --accent-gold:#d4af37; 
    --success-green:#10b981;
    --error-red:#ef4444;
    --warning-orange:#f59e0b;
    --light-slate:#e2e8f0;
    --pure-white:#ffffff;
    --dark-text:#0f172a;
    --border-gray:#94a3b8;
    --vb-toggle-overlap:8px;
}

/* ===============================
   SUPREME LIGHT THEME ENFORCEMENT
   Zero Dark Elements - Market Ready
   =============================== */

/* GLOBAL ROOT LIGHT THEME LOCK */
html, body, :root {
    color-scheme: light !important;
    --vb-bg: var(--pure-white);
    --vb-bg-2: #f1f5f9;
    --vb-text: var(--dark-text);
    background: var(--vb-bg) !important;
}

/* Accessible base theme — high contrast and brand colors */
/* App shell background kept light for readability */
.main { 
    background: #f8fafc; /* very light slate for neutral contrast */
    font-family: 'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; 
    color: var(--dark-text); 
}

/* Make sure the outer container is also light (prevents dark rims) */
[data-testid="stAppViewContainer"], html, body { 
    background: #f8fafc !important; 
    color-scheme: light !important; 
}

/* Force light theme colors at root to defeat in-app browser dark-mode (e.g., Instagram/FB) */
/* Explicitly set sidebar and containers to light surfaces */
[data-testid="stSidebar"], section[data-testid="stSidebar"] {
    background: var(--pure-white) !important; 
    color: var(--dark-text) !important;
}

.block-container, .stApp, [data-testid="stHeader"], [data-baseweb] {
    color-scheme: light !important;
}

[data-testid="stHeader"] { 
    background: #ffffff00 !important; 
}

/* Extra safety: keep all Streamlit panes and testid containers light */
[data-testid="stAppViewContainer"],
[data-testid^="st"],
[data-baseweb] {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
}

/* ===============================
   GLOBAL TEXT COLOR ENFORCEMENT
   Fix ALL faint/low-contrast text
   =============================== */
body, .stApp, .block-container,
[data-testid="stMarkdownContainer"],
h1, h2, h3, h4, h5, h6,
p, li, label, span, div,
code, pre, kbd, samp, strong, em {
    color: var(--dark-text) !important;
}

/* ===============================================
   SURGICAL WHITE ARTIFACT ELIMINATION
   Target Streamlit's default white boxes/borders
   =============================================== */

/* NUCLEAR: Remove ALL white boxes in sidebar */
section[data-testid="stSidebar"] .element-container,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* Remove white boxes around markdown elements */
[data-testid="stMarkdownContainer"],
.element-container {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Ensure sidebar itself has NO white boxes or weird padding */
section[data-testid="stSidebar"] {
    --vb-sidebar-divider-offset: 8px;
    background: #ffffff !important;
    border-right: none !important;
    overflow-y: auto !important;
    max-height: 100vh !important;
    position: relative !important;
}

section[data-testid="stSidebar"]::after {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    right: var(--vb-sidebar-divider-offset, 0px);
    width: 1px;
    background: #e2e8f0;
    pointer-events: none;
}

/* Ensure sidebar content wrapper allows scrolling */
section[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
    border: none !important;
    padding: 1rem !important;
    min-height: 100% !important;
    overflow-y: visible !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Remove padding/margin artifacts on all sidebar children */
section[data-testid="stSidebar"] * {
    box-sizing: border-box !important;
}

/* Clean up any remaining white artifact boxes */
[data-testid="stVerticalBlock"],
[class*="css-"],
.st-emotion-cache {
    background: transparent !important;
    border: none !important;
}

/* ===============================================
   END WHITE ARTIFACT ELIMINATION
   =============================================== */

/* ===============================
   BASEWEB & STREAMLIT COMPONENTS
   Neutralize ALL dark surfaces
   =============================== */
[data-baseweb], [data-testid], .st-emotion-cache { 
    color-scheme: light !important; 
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
}

[data-baseweb="select"] [role="combobox"],
[data-baseweb="popover"],
[data-baseweb="layer"],
[data-baseweb="modal"],
div[role="presentation"],
[data-baseweb="tooltip"],
.stTooltipIcon {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
}

/* Expander/accordion elements */
.streamlit-expanderHeader,
[data-testid="stExpander"],
details summary {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
    border: 1px solid var(--light-slate) !important;
}

/* Expanded content areas */
[data-testid="stExpander"] > div:last-child,
details[open] {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
}

/* Expander arrows: dark icons with rotate on expand */
[data-testid="stExpander"] summary svg,
.streamlit-expanderHeader svg {
    color: var(--dark-text) !important;
    transform: rotate(0deg) !important;
    transition: transform .2s ease !important;
}
[data-testid="stExpander"][aria-expanded="true"] summary svg,
.streamlit-expanderHeader[aria-expanded="true"] svg {
    transform: rotate(90deg) !important;
}

/* Info boxes and alerts kept light */
.stAlert, [data-baseweb="notification"] {
    background: #eff6ff !important;
    color: var(--dark-text) !important;
    border: 1px solid #93c5fd !important;
}

/* ===============================
   FILE UPLOADER - LIGHT THEME
   Ensure visible drop zone and labels
   =============================== */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] .uploadDropTarget,
.stFileUploader,
.stFileUploader section,
.stFileUploader .uploadDropTarget {
    background: #f8fafc !important; /* Slightly off-white for visibility */
    border: 3px dashed var(--primary-blue) !important; /* Thicker, brand-color border */
    color: var(--dark-text) !important;
    border-radius: 12px !important;
    padding: 2rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover,
.stFileUploader:hover {
    background: #eff6ff !important; /* Light blue tint on hover */
    border-color: var(--accent-gold) !important;
}

[data-testid="stFileUploader"] *,
.stFileUploader * { 
    color: var(--dark-text) !important; 
}

/* Uploader button itself - SUPREME VISIBILITY */
[data-testid="stFileUploader"] button,
.stFileUploader button {
    background: var(--primary-blue) !important;
    color: var(--pure-white) !important;
    border: 2px solid var(--primary-blue) !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    cursor: pointer !important;
    min-height: 44px !important;
    /* CRITICAL: Force text rendering */
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
}

/* CRITICAL: All children of Browse button must be white */
[data-testid="stFileUploader"] button *,
.stFileUploader button * {
    color: var(--pure-white) !important;
    fill: var(--pure-white) !important;
    -webkit-font-smoothing: antialiased !important;
}

[data-testid="stFileUploader"] button:hover,
.stFileUploader button:hover,
button[kind="secondary"]:hover {
    background: var(--accent-gold) !important;
    border-color: var(--accent-gold) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 12px rgba(0,0,0,0.15) !important;
    color: var(--pure-white) !important;
}

/* Caret visible on light background */
input, textarea { caret-color: var(--dark-text) !important; }

/* File uploader label text - make it VERY visible */
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] small,
.stFileUploader label,
.stFileUploader small {
    color: var(--dark-text) !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

/* ===============================
   FORM INPUTS - PRISTINE WHITE
   All text/email/password fields
   =============================== */
input[type="text"], 
input[type="email"], 
input[type="password"], 
input[type="number"],
input[type="search"],
textarea,
[data-baseweb="input"] input,
.stTextInput input, 
.stTextArea textarea,
.stNumberInput input {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
    border: 2px solid var(--border-gray) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
    transition: all 0.2s ease !important;
}

/* Input focus states */
input:focus, textarea:focus, select:focus {
    border-color: var(--primary-blue) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(26, 54, 93, 0.1) !important;
}

/* Input placeholders readable but subtle */
input::placeholder,
textarea::placeholder,
.stTextInput input::placeholder,
.stTextArea textarea::placeholder { 
    color: #64748b !important; 
    opacity: 1 !important;
}

/* Password visibility toggle (eye button) */
[data-baseweb="input"] svg, 
[data-baseweb="input"] button { 
    color: var(--dark-text) !important; 
    fill: var(--dark-text) !important; 
}

[data-baseweb="input"] button,
[data-baseweb="input"] [role="button"] {
    background: var(--pure-white) !important;
    border: 1px solid var(--border-gray) !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
}

[data-baseweb="input"] button:hover {
    background: #f8fafc !important;
    border-color: var(--primary-blue) !important;
}

/* Force all input wrappers light */
[data-baseweb="input"], 
.stTextInput, 
.stTextArea, 
.stPasswordInput,
.stNumberInput {
    background: var(--pure-white) !important;
}

/* ===============================
   SELECT/DROPDOWN - LIGHT THEME
   All dropdown components
   =============================== */
[data-baseweb="select"],
[data-baseweb="popover-inner"],
.stSelectbox,
select {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
    border-radius: 8px !important;
}

[data-baseweb="select"] > div,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] [role="button"] {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
    border: 2px solid var(--border-gray) !important;
    border-radius: 8px !important;
}

/* Dropdown menu lists */
[role="listbox"], 
[role="menu"], 
[data-baseweb="menu"],
[data-baseweb="popover"] {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    border: 1px solid var(--light-slate) !important;
}

[role="option"], 
[role="menuitem"] {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
    padding: 0.5rem 1rem !important;
}

[role="option"]:hover, 
[role="menuitem"]:hover,
[role="option"][aria-selected="true"] {
    background: #f1f5f9 !important;
    color: var(--primary-blue) !important;
}

/* ===============================
   CHECKBOXES & RADIO BUTTONS
   Light theme styling
   =============================== */
/* Checkbox styling */
input[type="checkbox"],
.stCheckbox input[type="checkbox"],
[data-baseweb="checkbox"] {
    background: var(--pure-white) !important;
    border: 2px solid var(--border-gray) !important;
    border-radius: 4px !important;
    width: 20px !important;
    height: 20px !important;
    cursor: pointer !important;
}

input[type="checkbox"]:checked,
.stCheckbox input[type="checkbox"]:checked {
    background: var(--primary-blue) !important;
    border-color: var(--primary-blue) !important;
}

input[type="checkbox"]:hover {
    background: #dbeafe !important;
    border-color: var(--primary-blue) !important;
}

/* Radio button styling */
input[type="radio"],
.stRadio input[type="radio"],
[data-baseweb="radio"] {
    background: var(--pure-white) !important;
    border: 2px solid var(--border-gray) !important;
    width: 20px !important;
    height: 20px !important;
    cursor: pointer !important;
}

input[type="radio"]:checked {
    background: var(--primary-blue) !important;
    border-color: var(--primary-blue) !important;
}

input[type="radio"]:hover {
    background: #dbeafe !important;
    border-color: var(--primary-blue) !important;
}

/* Radio/Checkbox labels */
.stCheckbox,
.stRadio:not(section[data-testid="stSidebar"] .stRadio),
.stCheckbox label,
.stRadio:not(section[data-testid="stSidebar"] .stRadio) label,
[data-baseweb="checkbox"],
[data-baseweb="radio"]:not(section[data-testid="stSidebar"] [data-baseweb="radio"]),
[data-baseweb="checkbox"] + label,
[data-baseweb="radio"]:not(section[data-testid="stSidebar"] [data-baseweb="radio"]) + label {
    color: var(--dark-text) !important;
    font-weight: 500 !important;
    margin-left: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 0.5rem !important;
    margin-bottom: 0.75rem !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
}

/* Ensure checkbox/radio containers don't force column layout */
.stCheckbox > div,
.stRadio:not(section[data-testid="stSidebar"] .stRadio) > div {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 0.5rem !important;
    flex-wrap: nowrap !important;
}

/* Ensure checkbox/radio text content flows horizontally */
.stCheckbox label > div,
.stCheckbox label > span,
.stRadio:not(section[data-testid="stSidebar"] .stRadio) label > div,
.stRadio:not(section[data-testid="stSidebar"] .stRadio) label > span {
    display: inline-block !important;
    white-space: nowrap !important;
    line-height: 1.5 !important;
    vertical-align: middle !important;
}

/* Ensure radio buttons in sidebar navigation are properly visible - NO WHITE ARTIFACTS */
section[data-testid="stSidebar"] .stRadio,
section[data-testid="stSidebar"] .stRadio > div,
section[data-testid="stSidebar"] [role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.75rem !important;
    width: 100% !important;
    visibility: visible !important;
    opacity: 1 !important;
    margin-bottom: 1rem !important;
    background: transparent !important;
}

/* Remove ALL white backgrounds from navigation containers */
section[data-testid="stSidebar"] .stRadio *,
section[data-testid="stSidebar"] [role="radiogroup"] *,
section[data-testid="stSidebar"] .stRadio > div > div,
section[data-testid="stSidebar"] [role="radiogroup"] > div {
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
}

/* Add Navigation section header styling */
section[data-testid="stSidebar"] .stRadio > label:first-child,
section[data-testid="stSidebar"] [role="radiogroup"] > div:first-child {
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    color: var(--dark-text) !important;
    margin-bottom: 0.75rem !important;
    padding-bottom: 0.5rem !important;
    border-bottom: 2px solid var(--light-slate) !important;
    display: block !important;
}

/* Radio button items should stack vertically with proper spacing - TRANSPARENT BY DEFAULT */
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] [role="radio"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    padding: 0.75rem 0.5rem !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    white-space: normal !important;
    word-wrap: break-word !important;
}

/* Ensure label text content is properly contained */
section[data-testid="stSidebar"] .stRadio label > div,
section[data-testid="stSidebar"] .stRadio label > span,
section[data-testid="stSidebar"] [role="radio"] > div,
section[data-testid="stSidebar"] [role="radio"] > span {
    flex: 1 !important;
    display: inline-block !important;
    line-height: 1.4 !important;
    color: var(--dark-text) !important;
}

section[data-testid="stSidebar"] .stRadio label:hover,
section[data-testid="stSidebar"] [role="radio"]:hover {
    background: rgba(26, 54, 93, 0.08) !important;
    transform: translateX(2px) !important;
}

/* Highlight selected radio option */
section[data-testid="stSidebar"] .stRadio label:has(input:checked),
section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
    background: linear-gradient(135deg, rgba(26, 54, 93, 0.1) 0%, rgba(26, 54, 93, 0.05) 100%) !important;
    border-left: 3px solid var(--primary-blue) !important;
    font-weight: 600 !important;
}

/* Ensure radio input is visible and styled */
section[data-testid="stSidebar"] .stRadio input[type="radio"],
section[data-testid="stSidebar"] [role="radio"] input {
    flex-shrink: 0 !important;
    margin-right: 0.75rem !important;
    width: 20px !important;
    height: 20px !important;
    visibility: visible !important;
    opacity: 1 !important;
    accent-color: var(--primary-blue) !important;
    position: relative !important;
    z-index: 1 !important;
}

/* ===============================
   BADGES & CHIPS - LIGHT DESIGN
   Elegant status indicators
   =============================== */
[data-baseweb="tag"],
.stBadge, .badge, .chip,
span[data-baseweb="tag"] {
    background: var(--light-slate) !important;
    color: var(--dark-text) !important;
    border: 1px solid var(--border-gray) !important;
    padding: 0.25rem 0.75rem !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
}

/* Success/info badges and checkmarks */
.badge-success, 
[data-baseweb="tag"].success,
.vb-chip.ok {
    background: #d1fae5 !important;
    color: #065f46 !important;
    border-color: var(--success-green) !important;
}

.badge-info,
.vb-chip.info {
    background: #dbeafe !important;
    color: #1e40af !important;
    border-color: var(--primary-blue) !important;
}

.vb-chip.warn {
    background: #fef3c7 !important;
    color: #92400e !important;
    border-color: var(--warning-orange) !important;
}

.vb-chip.err {
    background: #fee2e2 !important;
    color: #991b1b !important;
    border-color: var(--error-red) !important;
}

/* ===============================
   AUDIO CONTROLS - LIGHT THEME
   Remove ALL dark native UI
   =============================== */
audio, 
audio::-webkit-media-controls-panel,
audio::-webkit-media-controls-enclosure {
    background: var(--pure-white) !important;
    color-scheme: light !important;
    border-radius: 8px !important;
    border: 1px solid var(--light-slate) !important;
}

/* Ensure audio control buttons are visible */
audio::-webkit-media-controls-play-button,
audio::-webkit-media-controls-pause-button,
audio::-webkit-media-controls-mute-button,
audio::-webkit-media-controls-volume-slider {
    filter: none !important;
    opacity: 1 !important;
}

/* Links use primary blue; hovered/active use gold for clear affordance */
a, a:visited { color: var(--primary-blue) !important; }
a:hover, a:focus { color: var(--accent-gold) !important; }

/* App container with elegant shadow */
.stApp { 
    background:white; 
    border-radius:20px; 
    box-shadow:0 25px 50px -12px rgba(0,0,0,.25); 
    margin:2rem; 
    min-height:90vh; 
}

/* ===============================================
   PRO RECORDER - COMPLETE LIGHT THEME
   Canvas, controls, and download elements
   =============================================== */

/* Recorder container - light background */
#vb_container,
.vb-recorder-container {
    background: var(--pure-white) !important;
    border: 1px solid var(--light-slate) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}

/* Control buttons styling */
#vb_controls,
.vb-recorder-controls {
    display: flex !important;
    gap: 0.75rem !important;
    margin: 1rem 0 !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Start recording button - brand blue with white text */
#vb_start,
button[id*="start"],
.vb-btn-start {
    background: linear-gradient(135deg, var(--primary-blue) 0%, #2d3748 100%) !important;
    color: var(--pure-white) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    min-width: 140px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
}

#vb_start:hover {
    background: linear-gradient(135deg, #2d3748 0%, var(--primary-blue) 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 12px rgba(0,0,0,0.15) !important;
}

#vb_start:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Stop recording button - red with white text */
#vb_stop,
button[id*="stop"],
.vb-btn-stop {
    background: linear-gradient(135deg, var(--error-red) 0%, #dc2626 100%) !important;
    color: var(--pure-white) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px rgba(239, 68, 68, 0.2) !important;
    min-width: 140px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
}

#vb_stop:hover {
    background: linear-gradient(135deg, #dc2626 0%, var(--error-red) 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 12px rgba(239, 68, 68, 0.3) !important;
}

#vb_stop:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Status and level text - dark readable text */
#vb_status,
#vb_level,
.vb-recorder-status,
.vb-recorder-level {
    color: var(--dark-text) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.5rem !important;
    background: #f8fafc !important;
    border-radius: 8px !important;
    margin: 0.5rem 0 !important;
    text-align: center !important;
}

/* Waveform canvas - light background */
#vb_canvas,
canvas[id*="canvas"],
.vb-waveform-canvas {
    background: var(--light-slate) !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 8px !important;
    width: 100% !important;
    height: auto !important;
    max-width: 100% !important;
    margin: 1rem 0 !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.05) !important;
}

/* Audio playback element - light theme */
#vb_play,
audio[id*="play"],
.vb-audio-player {
    background: var(--pure-white) !important;
    border: 1px solid var(--light-slate) !important;
    border-radius: 8px !important;
    width: 100% !important;
    margin: 1rem 0 !important;
    padding: 0.5rem !important;
    color-scheme: light !important;
}

/* Download link styling - prominent and light */
#vb_download_wrap,
.vb-download-wrapper {
    text-align: center !important;
    margin: 1rem 0 !important;
}

#vb_download,
a[id*="download"],
.vb-download-link {
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    background: var(--light-slate) !important;
    color: var(--primary-blue) !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 10px !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    border: 2px solid var(--border-gray) !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
}

#vb_download:hover,
a[id*="download"]:hover,
.vb-download-link:hover {
    background: #cbd5e1 !important;
    border-color: var(--primary-blue) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    color: var(--primary-blue) !important;
}

/* Ensure recorder iframe backgrounds are light */
iframe[title*="recorder"],
iframe[src*="component"] {
    background: var(--pure-white) !important;
    border: none !important;
    border-radius: 12px !important;
}

}

/* Explicit labels that must always be white on blue */
[data-testid="stFormSubmitButton"] button span:where(:not(:empty)),
[data-testid="stButton"] button span:where(:not(:empty)) {
    color: var(--pure-white) !important;
}

/* ===============================
   DOWNLOAD & LINK BUTTONS
   Consistent white text on brand buttons
   =============================== */
.stDownloadButton>button {
    color: var(--dark-text) !important;
    background: var(--light-slate) !important;
    border: 2px solid var(--border-gray) !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
}

.stDownloadButton>button * {
    color: var(--dark-text) !important;
    fill: var(--dark-text) !important;
}

/* Link buttons rendered as anchors */
.stLinkButton a,
.stLinkButton>a,
.stLinkButton button,
.stLinkButton [data-testid="baseButton-primary"] {
    color: var(--pure-white) !important;
    text-decoration: none !important;
}

[data-testid="stLinkButton"] a { 
    color: var(--pure-white) !important; 
}

/* ===============================
   BASE BUTTON - STREAMLIT UNIFIED
   Enforce white text for primary variants
   =============================== */
[data-testid="baseButton-primary"],
[data-testid="baseButton-primary"] * { 
    color: var(--pure-white) !important; 
    fill: var(--pure-white) !important;
}

[data-testid="baseButton-primary"],
[data-testid="baseButton-primary"] button,
[data-testid="stFormSubmitButton"] button,
.stButton>button,
button[data-testid="baseButton-primary"],
button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary-blue) 0%, #0b2344 100%) !important;
    color: var(--pure-white) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2.4rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 12px 24px rgba(26, 54, 93, 0.28) !important;
    transition: all 0.25s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
    min-height: 3.1rem !important;
    position: relative !important;
    overflow: hidden !important;
}

/* Eliminate white inner rectangle artifacts */
[data-testid="baseButton-primary"] > div,
[data-testid="baseButton-primary"] button > div,
[data-testid="stFormSubmitButton"] button > div,
.stButton>button > div,
button[data-testid="baseButton-primary"] > div,
button[kind="primary"] > div,
[data-testid="baseButton-primary"] > div > div,
[data-testid="baseButton-primary"] button > div > div,
[data-testid="stFormSubmitButton"] button > div > div,
.stButton>button > div > div,
button[data-testid="baseButton-primary"] > div > div,
button[kind="primary"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Ensure all inner content inherits white text */
[data-testid="baseButton-primary"] *,
[data-testid="baseButton-primary"] button *,
[data-testid="stFormSubmitButton"] button *,
.stButton>button *,
button[data-testid="baseButton-primary"] *,
button[kind="primary"] * {
    color: var(--pure-white) !important;
    fill: var(--pure-white) !important;
    background: transparent !important;
}

[data-testid="baseButton-primary"] button:hover,
.stButton>button:hover,
button[data-testid="baseButton-primary"]:hover,
button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 16px 32px rgba(26, 54, 93, 0.32) !important;
    background: linear-gradient(135deg, #0b2344 0%, var(--primary-blue) 100%) !important;
}

[data-testid="baseButton-primary"][aria-disabled="true"],
[data-testid="baseButton-primary"][aria-disabled="true"] button,
.stButton>button:disabled,
button[data-testid="baseButton-primary"]:disabled,
button[kind="primary"]:disabled {
    background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%) !important;
    box-shadow: none !important;
    opacity: 0.8 !important;
    transform: none !important;
    cursor: not-allowed !important;
}

[data-testid="baseButton-primary"] svg,
[data-testid="baseButton-primary"] path { 
    color: var(--pure-white) !important; 
    fill: var(--pure-white) !important; 
}

[data-testid="baseButton-primary"][aria-disabled="true"],
[data-testid="baseButton-primary"][aria-disabled="true"] * { 
    color: var(--pure-white) !important; 
    opacity: 0.6 !important; 
}

/* Secondary buttons - light style with dark text */
[data-testid="baseButton-secondary"],
button[kind="secondary"] {
    background: var(--pure-white) !important;
    color: var(--primary-blue) !important;
    border: 2px solid var(--primary-blue) !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

[data-testid="baseButton-secondary"]:hover,
button[kind="secondary"]:hover {
    background: #f8fafc !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}

/* Premium cards */
.premium-card { 
    background:white; 
    padding:2rem; 
    border-radius:16px; 
    box-shadow:0 10px 25px rgba(0,0,0,.05); 
    border:1px solid #e2e8f0; 
    margin:1rem 0;
    transition:all .3s ease;
}

.premium-card:hover {
    box-shadow:0 15px 30px rgba(0,0,0,.08);
    transform:translateY(-2px);
}

/* Supreme header */
.supreme-header { 
    font-size:2.5rem; 
    font-weight:700; 
    background:linear-gradient(135deg,var(--primary-blue) 0%, var(--accent-gold) 100%); 
    -webkit-background-clip:text; 
    -webkit-text-fill-color:transparent; 
    text-align:center; 
    margin-bottom:1rem; 
}

/* ===============================
   Brand Component Kit (Ultra Supreme)
   =============================== */
/* Button system */
.vb-btn { display:inline-flex; align-items:center; gap:.5rem; font-weight:700; border-radius:12px; padding:.7rem 1.25rem; border:2px solid transparent; cursor:pointer; text-decoration:none; }
.vb-btn--primary { background:linear-gradient(135deg,var(--primary-blue) 0%, #0b2344 100%); color:#ffffff !important; }
.vb-btn--primary:hover { filter:brightness(1.05); box-shadow:0 8px 18px rgba(26,54,93,.25); }
.vb-btn--secondary { background:#ffffff; color:var(--primary-blue); border-color:var(--primary-blue); }
.vb-btn--secondary:hover { background:#f8fafc; }
.vb-btn--tertiary { background:transparent; color:var(--primary-blue); }
.vb-btn:disabled, .vb-btn[disabled] { opacity:.5; cursor:not-allowed; box-shadow:none; }

/* Section headers */
.vb-section-title { font-size:1.5rem; font-weight:800; color:#0f172a; border-left:6px solid var(--accent-gold); padding-left:.6rem; margin:.25rem 0 .75rem; }

/* Stat cards */
.vb-stat { text-align:center; }
.vb-stat .vb-stat__value { font-size:2.2rem; font-weight:800; margin:0; }
.vb-stat .vb-stat__label { font-weight:700; margin:.5rem 0 0 0; }
.vb-stat .vb-stat__sub { font-size:.9rem; margin:.25rem 0 0 0; }
.vb-stat--success { background: linear-gradient(135deg,#ecfdf5 0%,#d1fae5 100%); border:1px solid #10b981; }
.vb-stat--success .vb-stat__value { color:#064e3b; }
.vb-stat--success .vb-stat__label { color:#065f46; }
.vb-stat--success .vb-stat__sub { color:#047857; }
.vb-stat--info { background: linear-gradient(135deg,#eff6ff 0%,#dbeafe 100%); border:1px solid #1e40af; }
.vb-stat--info .vb-stat__value { color:#0f172a; }
.vb-stat--info .vb-stat__label { color:#1e3a8a; }
.vb-stat--info .vb-stat__sub { color:#1d4ed8; }
.vb-stat--brand { background: linear-gradient(135deg,#fff7ed 0%,#fde68a 100%); border:1px solid var(--accent-gold); }
.vb-stat--brand .vb-stat__value { color:#7c5a00; }
.vb-stat--brand .vb-stat__label { color:#6b4f00; }
.vb-stat--brand .vb-stat__sub { color:#8a5f00; }

/* Upgrade banner */
.vb-banner { border-radius:16px; padding:1.25rem; border:1px solid rgba(26,54,93,.12); }
.vb-banner--upgrade { background:linear-gradient(135deg, var(--primary-blue) 0%, #0b2344 100%); color:#fff; border-color:#0b2344; }
/* Override global text color: ensure ALL text inside the banner stays white */
.vb-banner--upgrade, .vb-banner--upgrade * { color:#ffffff !important; fill:#ffffff !important; }
.vb-banner--upgrade .vb-banner__title { font-weight:800; font-size:1.2rem; }
.vb-banner--upgrade .vb-banner__sub { opacity:.9; }

/* ===============================
   TABS - CLEAR SELECTION STATE
   Readable labels with visible active state
   =============================== */
div[data-testid="stTabs"] [role="tab"],
.stTabs [role="tab"],
div[data-baseweb="tab-list"] button,
[data-baseweb="tab"] button { 
    color: var(--dark-text) !important; 
    background: linear-gradient(135deg, rgba(226,232,240,0.95) 0%, rgba(203,213,225,0.95) 100%) !important; 
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    border: none !important;
    transition: all 0.2s ease !important;
    margin: 0 0.25rem !important;
    position: relative !important;
    overflow: hidden !important;
}

/* Unselected tab hover state */
div[data-testid="stTabs"] [role="tab"]:hover,
.stTabs [role="tab"]:hover,
div[data-baseweb="tab-list"] button:hover {
    background: linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%) !important;
    transform: translateY(-1px) !important;
}

/* Selected tab - brand blue background with white text */
div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
.stTabs [role="tab"][aria-selected="true"],
div[data-baseweb="tab-list"] button[aria-selected="true"],
[data-baseweb="tab"] button[aria-selected="true"] {
    background: linear-gradient(135deg, var(--primary-blue) 0%, #0b2344 100%) !important;
    color: var(--pure-white) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(26, 54, 93, 0.25) !important;
}

/* Remove white BaseWeb highlight slider and internal wrappers */
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-baseweb="tab-highlight"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

div[data-testid="stTabs"] > div:first-child,
div[data-testid="stTabs"] > div:first-child > div,
div[data-testid="stTabs"] > div:first-child > div > div,
div[data-testid="stTabs"] > div:first-child > div > div > div,
[data-baseweb="tab-list"],
[data-baseweb="tab-list"] > div,
[data-baseweb="tab-list"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

div[data-testid="stTabs"] [role="tab"]::before,
div[data-testid="stTabs"] [role="tab"]::after,
.stTabs [role="tab"]::before,
.stTabs [role="tab"]::after,
div[data-baseweb="tab"] button::before,
div[data-baseweb="tab"] button::after {
    display: none !important;
}

div[data-testid="stTabs"] [role="tab"] > div,
div[data-testid="stTabs"] [role="tab"] > div > div,
.stTabs [role="tab"] > div,
.stTabs [role="tab"] > div > div,
div[data-baseweb="tab"] button > div,
div[data-baseweb="tab"] button > div > div {
    background: transparent !important;
    box-shadow: none !important;
}

div[data-testid="stTabs"] [role="tab"][aria-selected="true"] > div,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] > div > div,
.stTabs [role="tab"][aria-selected="true"] > div,
.stTabs [role="tab"][aria-selected="true"] > div > div,
div[data-baseweb="tab"] button[aria-selected="true"] > div,
div[data-baseweb="tab"] button[aria-selected="true"] > div > div {
    color: var(--pure-white) !important;
}

/* Ensure inner text/icons in selected tabs are white */
.stTabs [role="tab"][aria-selected="true"] *,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] *,
div[data-baseweb="tab-list"] button[aria-selected="true"] *,
[data-baseweb="tab"] button[aria-selected="true"] * { 
    color: var(--pure-white) !important; 
    fill: var(--pure-white) !important; 
}

/* Ensure unselected tabs use dark readable text */
.stTabs [role="tab"]:not([aria-selected="true"]) *,
div[data-testid="stTabs"] [role="tab"]:not([aria-selected="true"]) *,
div[data-baseweb="tab-list"] button:not([aria-selected="true"]) * { 
    color: var(--dark-text) !important; 
}

/* Tab focus state for accessibility */
div[data-testid="stTabs"] [role="tab"]:focus,
.stTabs [role="tab"]:focus,
div[data-baseweb="tab-list"] button:focus { 
    outline: 3px solid var(--accent-gold) !important; 
    outline-offset: 2px !important; 
}

/* Ensure tab panels/content stay light */
[role="tabpanel"], 
.stTabs > div,
div[data-testid="stTabs"] > div > div { 
    background: var(--pure-white) !important; 
    color: var(--dark-text) !important;
    padding: 1.5rem !important;
    border-radius: 12px !important;
}

/* ===============================================
   MOBILE NAVIGATION - ROCK SOLID IMPLEMENTATION
   =============================================== */

/* Force hamburger menu to always be visible on mobile */
@media (max-width: 992px) {
    /* Make hamburger visible and sticky at top */
    [data-testid="stSidebarNavOpen"] { 
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 9999 !important; 
        display: block !important; 
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Style the hamburger button for maximum visibility */
    [data-testid="stSidebarNavOpen"] button { 
        width: 48px !important;
        height: 48px !important;
        opacity: 1 !important; 
        visibility: visible !important; 
        display: inline-flex !important; 
        align-items:center !important;
        justify-content:center !important;
        border-radius:12px !important;
        background: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,.15) !important;
        border: 2px solid var(--primary-blue) !important;
        transition: all .2s ease !important;
    }
    
    [data-testid="stSidebarNavOpen"] button:hover {
        background: var(--primary-blue) !important;
        transform: scale(1.05);
    }
    
    /* Ensure SVG icon is visible */
    [data-testid="stSidebarNavOpen"] svg { 
        opacity: 1 !important; 
        display:block !important;
        width: 24px !important;
        height: 24px !important;
        color: var(--primary-blue);
    }
    
    [data-testid="stSidebarNavOpen"] button:hover svg {
        color: white;
    }
    
    /* Hide any text and show custom icon if needed */
    [data-testid="stSidebarNavOpen"] button { 
        font-size: 0 !important; 
    }
    
    [data-testid="stSidebarNavOpen"] button::before { 
        content: "☰"; 
        font-size: 24px; 
        line-height: 1; 
        color: var(--primary-blue);
        display: block;
        position: absolute;
    }
    
    [data-testid="stSidebarNavOpen"] button:hover::before {
        color: white;
    }
    
    /* Ensure sidebar overlay sits above content AND properly sized */
    section[data-testid="stSidebar"] { 
        z-index: 9998 !important;
        box-shadow: 0 0 50px rgba(0,0,0,.3) !important;
        width: 21rem !important;
        max-width: 80vw !important;
        background: #ffffff !important;
        color: #0f172a !important;
    }
    
    /* Ensure sidebar content wrapper is properly visible */
    section[data-testid="stSidebar"] > div {
        width: 100% !important;
        height: 100% !important;
        padding: 1rem !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    
    /* Ensure all sidebar widgets and content are visible */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stRadio,
    section[data-testid="stSidebar"] .stButton,
    section[data-testid="stSidebar"] .stImage,
    section[data-testid="stSidebar"] [data-testid] {
        visibility: visible !important;
        opacity: 1 !important;
        display: block !important;
        color: #0f172a !important;
    }

    /* Ensure no accidental dimming on sidebar */
    section[data-testid="stSidebar"] * { filter: none !important; }
    
    /* Add padding to main content to avoid overlap with sticky hamburger */
    .block-container {
        padding-top: 4rem !important;
    }
}

/* On desktop/tablet widths, use standard layout */
@media (min-width: 993px) {
    [data-testid="stSidebarNavOpen"] { 
        position: relative !important;
    }
    
    /* Hide mobile hamburger menu on desktop */
    [data-testid="stSidebarNavOpen"] {
        display: none !important;
    }
}

/* ===============================================
   DESKTOP SIDEBAR COLLAPSE BUTTON FIX - ULTRA ROBUST
   =============================================== */
@media (min-width: 993px) {
    /* Target Streamlit's native collapse button in sidebar header */
    [data-testid="stSidebar"] button[kind="header"],
    section[data-testid="stSidebar"] > div > button[kind="header"] {
        visibility: visible !important;
        opacity: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        width: 40px !important;
        height: 40px !important;
        background: var(--primary-blue) !important;
        border-radius: 8px !important;
        color: white !important;
        transition: all 0.3s ease !important;
        margin: 0.5rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        z-index: 1000 !important;
    }
    
    /* Hide default SVG icon and add custom text */
    [data-testid="stSidebar"] button[kind="header"] svg {
        display: none !important;
    }
    
    /* Show "<<" when sidebar is open */
    [data-testid="stSidebar"] button[kind="header"]::before {
        content: "«" !important;
        font-size: 24px !important;
        font-weight: bold !important;
        color: white !important;
        line-height: 1 !important;
        position: absolute !important;
    }
    
    /* Hover effect for collapse button */
    [data-testid="stSidebar"] button[kind="header"]:hover {
        background: var(--accent-gold) !important;
        transform: scale(1.05) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    
    /* Style for expand button when sidebar is collapsed */
    [data-testid="collapsedControl"],
    div[data-testid="collapsedControl"] {
        position: fixed !important;
        left: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 999999 !important;
        visibility: visible !important;
        opacity: 1 !important;
        display: block !important;
        width: auto !important;
        height: auto !important;
    }
    
    /* The expand button itself */
    [data-testid="collapsedControl"] button,
    div[data-testid="collapsedControl"] > button {
        visibility: visible !important;
        opacity: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        width: 40px !important;
        height: 60px !important;
        background: var(--primary-blue) !important;
        color: white !important;
        border: none !important;
        border-radius: 0 8px 8px 0 !important;
        padding: 0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    /* Hide default SVG in expand button */
    [data-testid="collapsedControl"] button svg,
    div[data-testid="collapsedControl"] > button svg {
        display: none !important;
    }
    
    /* Show ">>" for expand button */
    [data-testid="collapsedControl"] button::before,
    div[data-testid="collapsedControl"] > button::before {
        content: "»" !important;
        font-size: 24px !important;
        font-weight: bold !important;
        color: white !important;
        line-height: 1 !important;
        position: absolute !important;
    }
    
    /* Hover effect for expand button */
    [data-testid="collapsedControl"] button:hover,
    div[data-testid="collapsedControl"] > button:hover {
        background: var(--accent-gold) !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.2) !important;
    }
}

/* ===============================================
   END MOBILE NAVIGATION
   =============================================== */

/* Elegant step dots / phase transitions */
.vb-steps { 
    display:flex; 
    gap:.5rem; 
    align-items:center; 
    justify-content:center; 
    margin: .5rem 0 1rem; 
}

.vb-step { 
    width:10px; 
    height:10px; 
    border-radius:50%; 
    background:#cbd5e1; 
    transition: transform .2s, background .2s; 
}

.vb-step.active { 
    background: var(--accent-gold); 
    transform: scale(1.2); 
    box-shadow: 0 0 0 4px rgba(212,175,55,.15); 
}

.vb-step.done { 
    background:#22c55e; 
}

/* Compact status chips */
.vb-chiprow { 
    display:flex; 
    flex-wrap:wrap; 
    gap:.4rem .5rem; 
}

.vb-chip { 
    display:inline-flex; 
    align-items:center; 
    gap:.35rem; 
    padding:.3rem .6rem; 
    border-radius:999px; 
    font-weight:600; 
    font-size:.85rem; 
    border:1px solid; 
    white-space:nowrap;
    transition: all .2s ease;
}

.vb-chip:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,.1);
}

.vb-chip .dot { 
    width:8px; 
    height:8px; 
    border-radius:50%; 
    background:currentColor; 
    opacity:.7; 
}

.vb-chip.ok { 
    background:#ecfdf5; 
    color:#065f46; 
    border-color:#a7f3d0; 
}

.vb-chip.warn { 
    background:#fffbeb; 
    color:#92400e; 
    border-color:#fde68a; 
}

.vb-chip.err { 
    background:#fef2f2; 
    color:#991b1b; 
    border-color:#fecaca; 
}

/* VocalBrand cards */
.vb-card { 
    background:white; 
    border:1px solid #e5e7eb; 
    border-radius:14px; 
    padding:1rem; 
    box-shadow: 0 6px 16px rgba(0,0,0,.06);
    transition: all .3s ease;
}

.vb-card:hover {
    box-shadow: 0 10px 20px rgba(0,0,0,.1);
    transform: translateY(-2px);
}

/* Sidebar polish */
section[data-testid="stSidebar"] .stButton,
section[data-testid="stSidebar"] .stButton>button { 
    visibility: visible !important;
    opacity: 1 !important;
    display: block !important;
    width: 100%; 
    background: linear-gradient(135deg, var(--primary-blue) 0%, #0b2344 100%) !important;
    color: var(--pure-white) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 1.5rem !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 16px rgba(26, 54, 93, 0.2) !important;
    transition: all 0.25s ease !important;
    text-align: center !important;
    cursor: pointer !important;
}

section[data-testid="stSidebar"] .stButton>button:hover { 
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 12px 20px rgba(26, 54, 93, 0.28) !important;
    background: linear-gradient(135deg, #0b2344 0%, var(--primary-blue) 100%) !important;
}

section[data-testid="stSidebar"] .stButton>button *,
section[data-testid="stSidebar"] .stButton>button span,
section[data-testid="stSidebar"] .stButton>button div,
section[data-testid="stSidebar"] .stButton>button p {
    color: var(--pure-white) !important;
    visibility: visible !important;
    opacity: 1 !important;
}

section[data-testid="stSidebar"] img { 
    width: 100% !important; 
    height: auto !important; 
}

section[data-testid="stSidebar"] { 
    padding-right: .5rem; 
}

/* Loading spinner enhancement */
.stSpinner > div {
    border-color: var(--accent-gold) !important;
    border-top-color: transparent !important;
}

/* Success/Error message styling */
.stSuccess,
.stSuccess .element-container,
[data-testid="stSuccess"],
[data-testid="stSuccess"] .element-container {
    background: linear-gradient(90deg, #ecfdf5 0%, #d1fae5 100%) !important;
    border-left: 4px solid var(--success-green) !important;
    border-radius: 8px !important;
    animation: slideIn .3s ease !important;
    color: #064e3b !important;
    box-shadow: none !important;
    border-right: none !important;
    border-top: none !important;
    border-bottom: none !important;
}

.stError,
.stError .element-container,
[data-testid="stException"],
[data-testid="stException"] .element-container {
    background: linear-gradient(90deg, #fef2f2 0%, #fee2e2 100%) !important;
    border-left: 4px solid var(--error-red) !important;
    border-radius: 8px !important;
    animation: slideIn .3s ease !important;
    color: #7f1d1d !important;
    box-shadow: none !important;
    border-right: none !important;
    border-top: none !important;
    border-bottom: none !important;
}

.stWarning,
.stWarning .element-container,
[data-testid="stWarning"],
[data-testid="stWarning"] .element-container {
    background: linear-gradient(90deg, #fffbeb 0%, #fef3c7 100%) !important;
    border-left: 4px solid var(--warning-orange) !important;
    border-radius: 8px !important;
    animation: slideIn .3s ease !important;
    color: #78350f !important;
    box-shadow: none !important;
    border-right: none !important;
    border-top: none !important;
    border-bottom: none !important;
}

.stInfo,
.stInfo .element-container,
[data-testid="stInfo"],
[data-testid="stInfo"] .element-container {
    background: linear-gradient(90deg, #eff6ff 0%, #dbeafe 100%) !important;
    border-left: 4px solid var(--primary-blue) !important;
    border-radius: 8px !important;
    animation: slideIn .3s ease !important;
    color: #0f172a !important;
    box-shadow: none !important;
    border-right: none !important;
    border-top: none !important;
    border-bottom: none !important;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Form inputs enhancement */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 8px;
    border: 2px solid #e5e7eb;
    transition: all .2s ease;
    background: #ffffff !important;
    color: #0f172a !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 3px rgba(26, 54, 93, .1);
}

/* Input placeholders readable but subtle */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder { color: #64748b !important; }

/* Selects and number inputs */
select, input[type="number"], input[type="search"] { color: #0f172a !important; background:#ffffff !important; }
select:focus, input[type="number"]:focus, input[type="search"]:focus { outline: 3px solid rgba(26,54,93,.25); }

/* Ensure overlay is off by default in all views unless explicitly enabled */
.vb-nav-overlay { opacity: 0 !important; pointer-events: none !important; }

/* Expander styling */
.streamlit-expanderHeader {
    background: linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 8px;
    font-weight: 600;
    transition: all .2s ease;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 100%);
    transform: translateX(4px);
}

/* ===============================================
   GLOBAL SAFETY NET - ELIMINATE ALL DARK ELEMENTS
   Last line of defense against any dark surfaces
   =============================================== */

/* Force ALL unknown containers to light theme */
div, section, article, main, header, footer, aside {
    background-color: inherit !important;
}

/* Prevent ANY black or very dark backgrounds */
*[style*="background: black"],
*[style*="background: #000"],
*[style*="background:#000"],
*[style*="background-color: black"],
*[style*="background-color: #000"],
*[style*="background-color:#000"],
*[style*="background: rgb(0, 0, 0)"],
*[style*="background-color: rgb(0, 0, 0)"] {
    background: var(--pure-white) !important;
}

/* Catch any remaining dark gray backgrounds */
*[style*="background: #1a1a1a"],
*[style*="background: #2d2d2d"],
*[style*="background: #333"],
*[style*="background-color: #1a1a1a"],
*[style*="background-color: #2d2d2d"],
*[style*="background-color: #333"] {
    background: var(--light-slate) !important;
}

/* NUCLEAR OPTION: Force ALL button text to be white - ULTRA AGGRESSIVE */
button,
button *,
button span,
button div,
button p,
.stButton button,
.stButton button *,
.stButton button span,
.stButton button div,
.stButton button p,
[data-testid="stButton"] button,
[data-testid="stButton"] button *,
[data-testid*="button"] button,
[data-testid*="button"] button *,
[class*="stButton"] button,
[class*="stButton"] button *,
button[style*="background: linear-gradient"],
button[style*="background: linear-gradient"] *,
button[style*="background: #1a365d"],
button[style*="background: #1a365d"] *,
button[style*="background: #2d3748"],
button[style*="background: #2d3748"] * {
    color: var(--pure-white) !important;
    fill: var(--pure-white) !important;
    -webkit-text-fill-color: var(--pure-white) !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    text-rendering: optimizeLegibility !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Override ANY Streamlit inline styles that hide text */
button[style*="color: transparent"],
button *[style*="color: transparent"],
.stButton button[style*="color: transparent"],
.stButton button *[style*="color: transparent"] {
    color: var(--pure-white) !important;
    -webkit-text-fill-color: var(--pure-white) !important;
}

/* Ensure button backgrounds are never transparent when they should be blue */
button[class*="st"],
[data-testid*="button"] button,
.stButton button {
    background: linear-gradient(135deg, var(--primary-blue) 0%, #2d3748 100%) !important;
}

/* Force visibility of all interactive elements */
button, a, input, select, textarea {
    opacity: 1 !important;
    visibility: visible !important;
}

/* Ensure SVG icons are never invisible */
svg, svg path, svg circle, svg rect {
    opacity: 1 !important;
    visibility: visible !important;
}

/* Contact form specific - light theme enforcement */
form, 
.stForm,
[data-testid="stForm"] {
    background: var(--pure-white) !important;
    border: 1px solid var(--light-slate) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}

/* Ensure modals and overlays are light */
[role="dialog"],
[role="alertdialog"],
.modal,
.overlay {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
}

/* Tooltips must be light with dark text */
[role="tooltip"],
.tooltip {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
    border: 1px solid var(--light-slate) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}

/* Loading spinners and progress indicators */
.stSpinner,
[data-testid="stSpinner"] {
    color: var(--primary-blue) !important;
    border-color: var(--accent-gold) !important;
}

/* Ensure all Streamlit widgets are light */
.stSlider,
.stColorPicker,
.stDateInput,
.stTimeInput {
    background: var(--pure-white) !important;
    color: var(--dark-text) !important;
}

/* ===============================================
   END GLOBAL SAFETY NET
   =============================================== */

/* Slightly tighter spacing in narrow screens */
@media (max-width: 640px) {
    .vb-card { padding: .75rem; }
    .premium-card { padding: 1rem; }
    .stApp { margin: 1rem; }
    
    /* Make buttons more touch-friendly on mobile */
    .stButton>button {
        min-height: 48px;
        font-size: 1.05rem;
    }
}

/* Hide Streamlit toolbar for cleaner UI */
[data-testid="stToolbar"] { 
    display: none !important; 
}

/* Floating action button (backup mobile menu) */
.vb-fab-menu { 
    display: none !important; 
}

@media (max-width: 992px) {
    .vb-fab-menu { 
        position: fixed; 
        right: max(1rem, env(safe-area-inset-right) + 1rem); 
        bottom: max(1rem, env(safe-area-inset-bottom) + 1rem); 
        z-index: 9999; 
        width: 56px; 
        height: 56px; 
        border: none; 
        border-radius: 50%; 
        cursor: pointer; 
        display: flex !important; 
        align-items: center; 
        justify-content: center; 
        color: #fff; 
        background: linear-gradient(135deg,var(--primary-blue) 0%, #2d3748 100%); 
        box-shadow: 0 10px 25px rgba(0,0,0,.2);
        transition: all .3s ease;
        -webkit-tap-highlight-color: transparent;
        user-select: none;
    }
    
    .vb-fab-menu:hover {
        transform: scale(1.1) rotate(90deg);
        box-shadow: 0 15px 30px rgba(0,0,0,.3);
    }
    
    .vb-fab-menu:active {
        transform: scale(0.95) rotate(90deg);
        box-shadow: 0 8px 20px rgba(0,0,0,.25);
    }
    
    .vb-fab-menu:focus { 
        outline: 3px solid rgba(212,175,55,.55); 
        outline-offset: 2px; 
    }
    
    .vb-fab-menu::after { 
        content: "☰"; 
        font-size: 24px;
        transition: transform .3s ease;
    }
    
    .vb-fab-menu:hover::after {
        transform: rotate(-90deg);
    }
    
    /* Pulse animation to draw attention */
    @keyframes fabPulse {
        0%, 100% { box-shadow: 0 10px 25px rgba(0,0,0,.2); }
        50% { box-shadow: 0 10px 25px rgba(0,0,0,.2), 0 0 0 8px rgba(26, 54, 93, .15); }
    }
    
    .vb-fab-menu.pulse {
        animation: fabPulse 2s ease-in-out infinite;
    }
}

/* Ensure main app content and header do not overlay the forced-open sidebar */
[data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
    z-index: auto !important;
}

/* Pulse animation for important CTAs */
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

.pulse-cta {
    animation: pulse 2s ease-in-out infinite;
}

/* ===============================
   Desktop persistent toggle button
   =============================== */
@media (min-width: 993px) {
    #vb-desktop-toggle.vb-desktop-toggle {
        position: fixed;
        left: 0; /* will be overridden by the alignment helper later */
        top: 50%;
        transform: translateY(-50%);
        z-index: 1000000;
        width: 44px;
        height: 64px;
        border: none;
        border-radius: 0 10px 10px 0;
        background: var(--primary-blue);
        color: #fff;
        font-size: 26px;
        font-weight: 700;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 16px rgba(0,0,0,.2);
        cursor: pointer;
        transition: transform .2s ease, background .2s ease, box-shadow .2s ease;
        pointer-events: auto !important; /* ensure clicks always reach the button */
    }
    #vb-desktop-toggle.vb-desktop-toggle:hover {
        background: var(--accent-gold);
        box-shadow: 0 10px 24px rgba(0,0,0,.25);
        transform: translateY(-50%) scale(1.05);
    }
    /* Symbols controlled by checkbox state to avoid duplicates */
    #vb-desktop-toggle.vb-desktop-toggle::before { content: "«"; }
    :root:has(#vb-desktop-chk:checked) #vb-desktop-toggle.vb-desktop-toggle::before { content: "»"; }

    /* Ultra-supreme: drive desktop sidebar purely via a CSS class + var */
    :root { --vb-sidebar-w: 21rem; }
    /* Sidebar OPEN when checkbox is unchecked */
    :root:not(:has(#vb-desktop-chk:checked)) [data-testid="stSidebar"],
    :root:not(:has(#vb-desktop-chk:checked)) section[data-testid="stSidebar"] {
        position: sticky !important;
        top: 0 !important;
        left: 0 !important;
        transform: translateX(0) !important;
        width: var(--vb-sidebar-w) !important;
        min-width: var(--vb-sidebar-w) !important;
        max-width: var(--vb-sidebar-w) !important;
        height: 100vh !important;
        z-index: 1 !important;
    }
    /* Sidebar CLOSED when checkbox is checked */
    :root:has(#vb-desktop-chk:checked) [data-testid="stSidebar"],
    :root:has(#vb-desktop-chk:checked) section[data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        transform: translateX(calc(-1 * var(--vb-sidebar-w))) !important;
        width: var(--vb-sidebar-w) !important;
        min-width: var(--vb-sidebar-w) !important;
        max-width: var(--vb-sidebar-w) !important;
        height: 100vh !important;
        z-index: 9999 !important;
    }
}
@media (max-width: 992px) {
    #vb-desktop-toggle.vb-desktop-toggle { display: none !important; }
}

/* ========================================
   🎯 WHITE ARTIFACT ELIMINATION RULES
   SURGICAL CSS ADDITIONS - DO NOT MODIFY
   ======================================== */

/* 🎯 WHITE ARTIFACT FIX #1: Info boxes with instructions (blue background sections) */
.stAlert, div[data-baseweb="notification"] {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #2: Upload file sections (dashed border areas) */
section[data-testid="stFileUploader"] > div,
section[data-testid="stFileUploader"] > div > div {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #3: Error/Warning message boxes */
.stAlert > div,
div[role="alert"] {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #4: Success message containers */
.element-container div[data-testid="stMarkdownContainer"] > div,
.stSuccess {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #5: Call-to-action banner sections */
div[data-testid="stHorizontalBlock"] > div > div > div {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #6: Recording interface instruction boxes */
div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #7: Contact form header section */
div[data-testid="column"] > div > div > div[data-testid="stVerticalBlock"] {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #8: Generic container backgrounds that appear white */
.element-container > div:first-child {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #9: Streamlit default white backgrounds on markdown containers */
div[data-testid="stMarkdownContainer"] {
    background: transparent !important;
    background-color: transparent !important;
}

/* 🎯 WHITE ARTIFACT FIX #10: Audio player containers - VISIBLE & STYLED */
div[data-testid="stAudioPlayer"] {
    background: transparent !important;
    background-color: transparent !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    height: auto !important;
    min-height: 54px !important;
    overflow: visible !important;
}

/* Ensure Streamlit audio player is always visible */
div[data-testid="stAudioPlayer"] audio,
div[data-testid="stAudioPlayer"] > div,
div[data-testid="stAudioPlayer"] * {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: var(--pure-white) !important;
    border-radius: 8px !important;
}

div[data-testid="stAudioPlayer"] audio {
    width: 100% !important;
    min-height: 54px !important;
    border: 1px solid var(--light-slate) !important;
    margin: 0.5rem 0 !important;
}

</style>
"""

def inject_css():
    """Inject the global VocalBrand styling and keep buttons fully legible."""
    st.markdown(SUPREME_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        :root, html, body { color-scheme: light !important; }

        /* ╔══════════════════════════════════════════════════════════════╗
           ║  🚀 SUPREME NAVIGATION MENU - WORLD CLASS TRANSFORMATION  ║
           ║  Eliminates borders, fixes text flow, creates magic ✨     ║
           ╚══════════════════════════════════════════════════════════════╝ */
        
        /* OBLITERATE the ugly bordered button look - make it INVISIBLE by default */
        section[data-testid="stSidebar"] .stRadio,
        section[data-testid="stSidebar"] .stRadio > div,
        section[data-testid="stSidebar"] .stRadio > div > div,
        section[data-testid="stSidebar"] [role="radiogroup"],
        section[data-testid="stSidebar"] [role="radiogroup"] > div,
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] .row-widget,
        section[data-testid="stSidebar"] [class*="stRadio"] [class*="css-"],
        section[data-testid="stSidebar"] [class*="stRadio"] [class*="st-emotion"] {
            background: transparent !important;
            background-color: transparent !important;
            background-image: none !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            outline: none !important;
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 0.25rem !important;
            width: 100% !important;
            /* CRITICAL: Allow scrolling if content exceeds viewport */
            max-height: none !important;
            overflow: visible !important;
        }
        
        /* ANNIHILATE all nested borders and backgrounds - TOTAL TRANSPARENCY */
        section[data-testid="stSidebar"] .stRadio *:not(label):not(input),
        section[data-testid="stSidebar"] [role="radiogroup"] *:not(label):not(input):not([role="radio"]) {
            background: transparent !important;
            background-color: transparent !important;
            background-image: none !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            outline: none !important;
        }
        
        /* 🎯 SUPREME LABEL STYLING - Clean, minimal, elegant, COMPACT, ALIGNED */
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] [role="radio"] {
            background: transparent !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 0.75rem !important;
            margin: 0 !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            
            /* Typography - Clear and Readable */
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            color: #475569 !important;
            letter-spacing: 0.01em !important;
            line-height: 1.3 !important;
            
            /* Layout - Force horizontal text flow */
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: 100% !important;
            min-height: 40px !important;
            
            /* Text flow enforcement */
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }
        
        /* ✨ HOVER - Subtle, sophisticated interaction */
        section[data-testid="stSidebar"] .stRadio label:hover,
        section[data-testid="stSidebar"] [role="radio"]:hover {
            background: rgba(26, 54, 93, 0.05) !important;
            border: none !important;
            transform: none !important;
            color: var(--primary-blue) !important;
            box-shadow: 0 2px 6px rgba(26, 54, 93, 0.08) !important;
        }
        
        /* 🌟 ACTIVE/SELECTED - Bold, premium, unmistakable, ALIGNED */
        section[data-testid="stSidebar"] .stRadio label:has(input:checked),
        section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
            background: linear-gradient(135deg, rgba(26, 54, 93, 0.1) 0%, rgba(26, 54, 93, 0.05) 100%) !important;
            border: none !important;
            border-left: 3px solid var(--primary-blue) !important;
            padding-left: calc(0.75rem - 3px) !important;
            font-weight: 600 !important;
            color: var(--primary-blue) !important;
            box-shadow: 0 2px 10px rgba(26, 54, 93, 0.12) !important;
            transform: none !important;
        }
        
        /* 🔘 Radio circle - Clean, visible, on-brand, COMPACT */
        section[data-testid="stSidebar"] .stRadio input[type="radio"] {
            width: 18px !important;
            height: 18px !important;
            margin: 0 0.625rem 0 0 !important;
            accent-color: var(--primary-blue) !important;
            flex-shrink: 0 !important;
            cursor: pointer !important;
        }
        
        /* 🔥 TEXT FLOW NUCLEAR FIX - Horizontal rendering enforced at ALL levels */
        section[data-testid="stSidebar"] .stRadio label > div,
        section[data-testid="stSidebar"] .stRadio label > span,
        section[data-testid="stSidebar"] [role="radio"] > div,
        section[data-testid="stSidebar"] [role="radio"] > span {
            background: transparent !important;
            border: none !important;
            line-height: 1.5 !important;
            color: inherit !important;
            
            /* CRITICAL: Inline display + flex for text */
            display: inline-flex !important;
            flex: 1 1 auto !important;
            flex-direction: row !important;
            align-items: center !important;
            
            /* Text rendering */
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
            min-width: 0 !important;
            max-width: 100% !important;
            
            /* Force horizontal text rendering */
            writing-mode: horizontal-tb !important;
            text-orientation: mixed !important;
        }
        
        /* 💥 DEEP NESTED TEXT FIX - Prevent ANY vertical stacking */
        section[data-testid="stSidebar"] .stRadio label > div > *,
        section[data-testid="stSidebar"] .stRadio label > span > *,
        section[data-testid="stSidebar"] .stRadio label p,
        section[data-testid="stSidebar"] .stRadio label div div,
        section[data-testid="stSidebar"] [role="radio"] > div > *,
        section[data-testid="stSidebar"] [role="radio"] > span > *,
        section[data-testid="stSidebar"] [role="radio"] p,
        section[data-testid="stSidebar"] [role="radio"] div div {
            display: inline !important;
            width: auto !important;
            max-width: none !important;
            white-space: nowrap !important;
            overflow: visible !important;
            background: transparent !important;
            border: none !important;
            writing-mode: horizontal-tb !important;
            text-orientation: mixed !important;
        }
        
        /* 🌪️ GLOBAL TEXT ORIENTATION ENFORCEMENT - No vertical text ANYWHERE */
        section[data-testid="stSidebar"] .stRadio *,
        section[data-testid="stSidebar"] [role="radiogroup"] * {
            writing-mode: horizontal-tb !important;
            text-orientation: mixed !important;
        }
        
        /* 🛡️ FLEX DIRECTION LOCK - Row for text, column for stack */
        section[data-testid="stSidebar"] .stRadio label *:not(input),
        section[data-testid="stSidebar"] [role="radio"] *:not(input) {
            flex-direction: row !important;
        }
        
        /* 🎨 NAVIGATION HEADER STYLING - "Navigation" label - COMPACT & ALIGNED */
        section[data-testid="stSidebar"] .stRadio > label:first-of-type,
        section[data-testid="stSidebar"] [role="radiogroup"] > label:first-of-type {
            font-weight: 700 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            color: #64748b !important;
            padding: 0.375rem 0.75rem 0.5rem !important;
            margin-bottom: 0.25rem !important;
            border-bottom: none !important;
            background: transparent !important;
        }
        
        /* 📜 CRITICAL: Enable sidebar scrolling when content overflows */
        section[data-testid="stSidebar"] {
            overflow-y: auto !important;
            overflow-x: hidden !important;
            height: 100vh !important;
            max-height: 100vh !important;
            padding: 1rem 0.5rem !important;
        }
        
        section[data-testid="stSidebar"] > div:first-child {
            overflow-y: auto !important;
            overflow-x: hidden !important;
            height: 100% !important;
            max-height: 100% !important;
            padding-bottom: 2rem !important;
        }
        
        /* 🎯 SUPREME ALIGNMENT FIX: Match navigation items with toggle button position */
        section[data-testid="stSidebar"] .stRadio {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        /* Align radio items to match the toggle button's visual line */
        section[data-testid="stSidebar"] .stRadio label {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        
        /* Ensure header aligns with items */
        section[data-testid="stSidebar"] .stRadio > label:first-of-type,
        section[data-testid="stSidebar"] [role="radiogroup"] > label:first-of-type {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        
        /* Perfect vertical alignment: all items same left edge */
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] [role="radio"] {
            margin-left: 0 !important;
            margin-right: 0 !important;
        }

        /* Sidebar cleanup */
        section[data-testid="stSidebar"] .element-container,
        section[data-testid="stSidebar"] [class*="st-emotion"],
        section[data-testid="stSidebar"] [class*="css-"],
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] ul,
        section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] div:not(.vb-banner):not([class*="stButton"]):not([class*="stImage"]) {
            background: transparent !important;
            border: none !important;
        }

        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] > div > div {
            background: transparent !important;
            border: none !important;
        }

        /* Form surfaces stay clean */
        .stForm,
        [data-testid="stForm"],
        .stForm .element-container,
        [data-testid="stForm"] .element-container {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        .stFormSubmitButton,
        [data-testid="stFormSubmitButton"],
        .stFormSubmitButton .element-container,
        [data-testid="stFormSubmitButton"] .element-container {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            box-shadow: none !important;
        }

        /* Password toggle button remains dark on light background */
        [data-baseweb="input"] button,
        [data-baseweb="input"] [role="button"] {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 6px !important;
            color: #0f172a !important;
            padding: 0.25rem 0.5rem !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }

        [data-baseweb="input"] button:hover,
        [data-baseweb="input"] [role="button"]:hover {
            background: #f8fafc !important;
            border-color: var(--primary-blue) !important;
        }

        [data-baseweb="input"] button *,
        [data-baseweb="input"] [role="button"] *,
        [data-baseweb="input"] button span,
        [data-baseweb="input"] [role="button"] span {
            color: #0f172a !important;
            fill: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
        }

        /* Tab containers should never inherit dark chrome */
        [data-testid="stTabs"],
        [data-testid="stTabs"] .element-container,
        [data-baseweb="tab-list"],
        [data-baseweb="tab-panel"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        form .element-container,
        form [class*="st-emotion"],
        form [class*="css-"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
                )

    # Ultra-supreme: place desktop toggle flush with sidebar edge (visual-only)
    st.markdown(
        """
        <style>
        @media (min-width: 993px) {
            :root { --vb-sidebar-w: 21rem; }
            /* When sidebar is OPEN (checkbox unchecked), move toggle to sidebar edge */
            :root:not(:has(#vb-desktop-chk:checked)) #vb-desktop-toggle.vb-desktop-toggle {
                left: calc(var(--vb-sidebar-w) - 8px) !important; /* slightly overlap for a neat seam */
                top: 50% !important;
                transform: translateY(-50%) !important;
            }
            /* When sidebar is CLOSED (checkbox checked), keep it at the left edge */
            :root:has(#vb-desktop-chk:checked) #vb-desktop-toggle.vb-desktop-toggle {
                left: 0 !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <script>
        (function() {
            const SELECTORS = [
                'button',
                'a[data-testid="stLinkButton"]',
                '[data-testid="baseButton-primary"]',
                '[data-testid="baseButton-secondary"]'
            ];
            const SELECTOR_STRING = SELECTORS.join(',');

            function parseColor(value) {
                if (!value) return null;
                const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([0-9.]+))?\)/i);
                if (!match) return null;
                return {
                    r: parseInt(match[1], 10),
                    g: parseInt(match[2], 10),
                    b: parseInt(match[3], 10),
                    a: match[4] === undefined ? 1 : parseFloat(match[4])
                };
            }

            function colorTone(el) {
                let current = el;
                for (let depth = 0; depth < 4 && current; depth += 1) {
                    const style = window.getComputedStyle(current);
                    const bgImage = (style.backgroundImage || '').toLowerCase();
                    if (bgImage && bgImage !== 'none') {
                        if (bgImage.includes('gradient') || bgImage.includes('#1a365d') || bgImage.includes('#2d3748') || bgImage.includes('#0b2344')) {
                            return 'dark';
                        }
                    }
                    const color = parseColor(style.backgroundColor);
                    if (color && color.a > 0) {
                        const brightness = (color.r * 299 + color.g * 587 + color.b * 114) / 1000;
                        return brightness < 170 ? 'dark' : 'light';
                    }
                    current = current.parentElement;
                }
                return 'light';
            }

            function shouldSkip(el) {
                return !!el.closest('[data-baseweb="input"]') || el.dataset.vbToneLocked === '1';
            }

            function applyTone(el, tone) {
                const textColor = tone === 'dark' ? 'var(--pure-white)' : 'var(--primary-blue)';
                el.style.setProperty('color', textColor, 'important');
                el.dataset.vbTone = tone;
                el.querySelectorAll('span, p, div, strong, em').forEach(node => {
                    node.style.setProperty('color', textColor, 'important');
                });
                el.querySelectorAll('svg, path, use').forEach(node => {
                    node.style.setProperty('color', textColor, 'important');
                    node.style.setProperty('fill', textColor, 'important');
                    node.style.setProperty('stroke', textColor, 'important');
                });
            }

            function update(el) {
                if (!(el instanceof HTMLElement)) return;
                if (!el.matches(SELECTOR_STRING)) return;
                if (shouldSkip(el)) return;
                applyTone(el, colorTone(el));
            }

            function process(root) {
                if (!root) return;
                if (root instanceof HTMLElement && root.matches(SELECTOR_STRING)) {
                    update(root);
                }
                const nodes = root.querySelectorAll ? root.querySelectorAll(SELECTOR_STRING) : [];
                nodes.forEach(update);
            }

            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.type === 'childList') {
                        mutation.addedNodes.forEach(node => process(node));
                    } else if (mutation.type === 'attributes') {
                        update(mutation.target);
                    }
                });
            });

            function init() {
                process(document.body);
                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['class', 'style', 'aria-selected', 'disabled']
                });
            }

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init, { once: true });
                window.addEventListener('load', init, { once: true });
            } else {
                init();
            }
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )
    
    # 🎯 INJECT TIKTOK BROWSER FIX
    # Detects TikTok in-app browser and warns users about microphone limitations
    inject_tiktok_browser_fix()

    # Additive-only UI fixes: sidebar divider alignment, nav radio alignment, and Pro Recorder audio reveal
    inject_supreme_sidebar_and_audio_fix()

def feature_columns(features: Iterable[str]):
    cols = st.columns(len(features))
    for col, feat in zip(cols, features):
        with col:
            st.markdown(feat)

def pro_feature_list():
    st.markdown("""
**Pro Features:**
- Unlimited voice generations
- Priority processing
- Commercial license
- Advanced voice controls
- 24/7 premium support
""")

def vb_stat_card(kind: str, value: str, label: str, sub: str = "") -> None:
    """Render a branded stat card inside a Streamlit column.
    kind: one of ['success','info','brand'] which maps to colorways.
    value: main number/text
    label: bold label line
    sub: optional subtext line
    """
    kind = (kind or "info").lower()
    cls = {
        "success": "vb-stat vb-card vb-stat--success",
        "brand": "vb-stat vb-card vb-stat--brand",
        "info": "vb-stat vb-card vb-stat--info",
    }.get(kind, "vb-stat vb-card vb-stat--info")
    html = f'''<div class="{cls}">
        <div>
            <h2 class="vb-stat__value">{value}</h2>
            <p class="vb-stat__label">{label}</p>
            {f'<p class="vb-stat__sub">{sub}</p>' if sub else ''}
        </div>
    </div>'''
    st.markdown(html, unsafe_allow_html=True)

def render_steps(active:int, total:int):
    """Render phase dots without changing navigation logic.
    active is 1-based index of the current step.
    """
    active = max(1, min(total, int(active or 1)))
    dots = []
    for i in range(1, total+1):
        cls = "vb-step"
        if i < active:
            cls += " done"
        elif i == active:
            cls += " active"
        dots.append(f'<span class="{cls}"></span>')
    st.markdown('<div class="vb-steps">' + "".join(dots) + '</div>', unsafe_allow_html=True)

def render_status_chips(items: Iterable[tuple[str, str, str]]):
    """Render compact status chips. items: (label, state[ok|warn|err], tooltip)."""
    chips = []
    for label, state, tip in items:
        state = state if state in {"ok","warn","err"} else "warn"
        chips.append(f'<span class="vb-chip {state}" title="{tip}"><span class="dot"></span>{label}</span>')
    st.markdown('<div class="vb-chiprow">' + "".join(chips) + '</div>', unsafe_allow_html=True)


def inject_mobile_nav_helpers():
    """Inject robust mobile navigation with multiple fallback mechanisms.
    
    This ensures the sidebar is ALWAYS accessible on mobile devices:
    1. Force-shows native Streamlit hamburger with enhanced styling
    2. Adds floating action button (FAB) as backup trigger
    3. Persistent monitoring to prevent CSS hiding issues
    4. Touch-optimized for best mobile UX
    """
    html = """
<!-- CSS-only mobile nav toggle: hidden checkbox controls sidebar and overlay -->
<input type="checkbox" id="vb-nav-toggle" class="vb-nav-toggle" aria-hidden="true" style="display:none" />
<label for="vb-nav-toggle" class="vb-fab-menu" id="vb-fab-menu" aria-label="Open navigation menu" title="Menu" tabindex="0"></label>
<label for="vb-nav-toggle" class="vb-nav-overlay" id="vb-nav-overlay" aria-hidden="true"></label>

<!-- Desktop-only persistent toggle (CSS-only using a hidden checkbox) -->
<input type="checkbox" id="vb-desktop-chk" class="vb-desktop-chk" aria-hidden="true" style="display:none" />
<label id="vb-desktop-toggle" class="vb-desktop-toggle" aria-label="Toggle sidebar" title="Toggle sidebar" for="vb-desktop-chk"></label>

<style>
/* CSS-only open state using :has() targeting Streamlit shells */
@media (max-width: 992px) {
    /* DEFAULT STATE: Sidebar completely hidden off-screen when NOT checked */
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        width: 21rem !important;
        max-width: 80vw !important;
        transform: translateX(-100%) !important; /* ✅ HIDE OFF-SCREEN */
        transition: transform 0.3s ease-in-out !important;
        z-index: 9998 !important;
        background: white !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        box-shadow: 0 0 50px rgba(0,0,0,.3) !important;
    }
    
    /* When our checkbox is checked, force sidebar visible and overlay on */
    body:has(#vb-nav-toggle:checked) [data-testid="stSidebar"],
    .main:has(#vb-nav-toggle:checked) [data-testid="stSidebar"],
    [data-testid="stAppViewContainer"]:has(#vb-nav-toggle:checked) [data-testid="stSidebar"] {
        transform: translateX(0) !important; /* ✅ SLIDE IN */
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        /* Put the sidebar absolutely on top of everything */
        z-index: 2147483647 !important; /* max int for safety */
    }
    
    /* Ensure sidebar CONTENT container is properly sized and visible */
    body:has(#vb-nav-toggle:checked) [data-testid="stSidebar"] > div,
    .main:has(#vb-nav-toggle:checked) [data-testid="stSidebar"] > div,
    [data-testid="stAppViewContainer"]:has(#vb-nav-toggle:checked) [data-testid="stSidebar"] > div {
        width: 100% !important;
        height: 100% !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        overflow-y: auto !important;
        padding: 1rem !important;
    }
    
    /* Ensure all sidebar child elements are visible */
    body:has(#vb-nav-toggle:checked) [data-testid="stSidebar"] * {
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Dim the page behind when open */
    body:has(#vb-nav-toggle:checked) .vb-nav-overlay,
    .main:has(#vb-nav-toggle:checked) .vb-nav-overlay,
    [data-testid="stAppViewContainer"]:has(#vb-nav-toggle:checked) .vb-nav-overlay {
        pointer-events: auto !important;
        opacity: .6 !important;
        z-index: 2147483646 !important; /* just below sidebar */
    }

    /* Overlay default (off) */
    .vb-nav-overlay {
        position: fixed; inset: 0; background: #000; opacity: 0; pointer-events: none;
        z-index: 9998;
        transition: opacity .2s ease;
        backdrop-filter: blur(2px);
    }

    /* Prevent background scroll when menu is open */
    body:has(#vb-nav-toggle:checked) {
        overflow: hidden !important;
    }

    /* Hide FAB while menu is open to avoid overlap */
    body:has(#vb-nav-toggle:checked) #vb-fab-menu {
        display: none !important;
    }
}
</style>
<script>
(function(){
    'use strict';
    // Hard lock Streamlit UI to light theme across sessions and in-app browsers
    try {
        const KEY = `stActiveTheme-${window.location.pathname}-v1`;
        // Remove any cached dark theme and set to Light
        const store = window.localStorage;
        if (store) {
            const raw = store.getItem(KEY);
            let needsSet = true;
            if (raw) {
                try { const parsed = JSON.parse(raw); needsSet = parsed?.name !== 'Light'; } catch {}
            }
            if (needsSet) {
                store.setItem(KEY, JSON.stringify({ name: 'Light' }));
            }
            // Clean legacy key as well
            const legacy = 'stActiveTheme';
            const legacyRaw = store.getItem(legacy);
            if (legacyRaw && legacyRaw.includes('Dark')) {
                store.removeItem(legacy);
            }
        }
        // Force prefers-color-scheme to light via meta tag (belt & braces)
    const meta = document.querySelector('meta[name="color-scheme"]') || document.createElement('meta');
    meta.setAttribute('name', 'color-scheme');
    meta.setAttribute('content', 'light');
    document.head.appendChild(meta);
    // Also set theme-color for Android/Chrome in-app browsers
    const themeMeta = document.querySelector('meta[name="theme-color"]') || document.createElement('meta');
    themeMeta.setAttribute('name', 'theme-color');
    themeMeta.setAttribute('content', '#ffffff');
    document.head.appendChild(themeMeta);
        // Also override if Streamlit exposes theme API
        if (window.__streamlit && window.__streamlit.setTheme) {
            window.__streamlit.setTheme('Light');
        }
    } catch (err) { console.warn('VocalBrand: theme lock failed', err); }
    
    // Configuration
    const MOBILE_BREAKPOINT = 992;
    const CHECK_INTERVAL = 800; // Check every 800ms for resilience
    
    // Detect mobile viewport
    function isMobileView() {
        return window.innerWidth <= MOBILE_BREAKPOINT;
    }
    
    // Get ALL possible DOM elements (Streamlit Cloud vs Local differences)
    function getElements() {
        return {
            fab: document.getElementById('vb-fab-menu'),
            // Try multiple selectors for hamburger
            hamburger: document.querySelector('[data-testid="stSidebarNavOpen"]') || 
                       document.querySelector('[data-testid="stSidebarNav"]') ||
                       document.querySelector('button[kind="header"]') ||
                       document.querySelector('.css-1544g2n') || // Streamlit Cloud class
                       document.querySelector('[aria-label*="navigation"]'),
            hamburgerBtn: document.querySelector('[data-testid="stSidebarNavOpen"] button') || 
                         document.querySelector('[data-testid="stSidebarNav"] button') ||
                         document.querySelector('button[kind="header"]'),
            sidebar: document.querySelector('[data-testid="stSidebar"]') ||
                    document.querySelector('section[data-testid="stSidebar"]') ||
                    document.querySelector('.css-1cypcdb') || // Streamlit Cloud sidebar class
                    document.querySelector('[role="complementary"]')
        };
    }
    
    // ULTRA-ROBUST sidebar opening - works on ALL Streamlit versions
    function openSidebar(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        console.log('VocalBrand: Attempting to open sidebar...');
        const els = getElements();
        const toggle = document.getElementById('vb-nav-toggle');

        // Ensure CSS-only fallback activates by forcing the toggle checked state
        if (toggle && !toggle.checked) {
            toggle.checked = true;
        }
        
        // Method 1: Direct button click (Streamlit standard)
        if (els.hamburgerBtn) {
            try {
                els.hamburgerBtn.click();
                console.log('VocalBrand: ✓ Sidebar opened via button.click()');
                return true;
            } catch (err) {
                console.warn('VocalBrand: Method 1 failed:', err);
            }
        }
        
        // Method 2: Dispatch multiple event types on button
        if (els.hamburgerBtn) {
            try {
                // Try click event
                const clickEvent = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                els.hamburgerBtn.dispatchEvent(clickEvent);
                
                // Also try pointerdown + pointerup (for touch simulation)
                const pointerDown = new PointerEvent('pointerdown', {
                    bubbles: true,
                    cancelable: true,
                    pointerId: 1,
                    pointerType: 'mouse'
                });
                const pointerUp = new PointerEvent('pointerup', {
                    bubbles: true,
                    cancelable: true,
                    pointerId: 1,
                    pointerType: 'mouse'
                });
                els.hamburgerBtn.dispatchEvent(pointerDown);
                els.hamburgerBtn.dispatchEvent(pointerUp);
                
                console.log('VocalBrand: ✓ Sidebar opened via dispatched events');
                return true;
            } catch (err) {
                console.warn('VocalBrand: Method 2 failed:', err);
            }
        }
        
        // Method 3: Click parent container
        if (els.hamburger) {
            try {
                els.hamburger.click();
                console.log('VocalBrand: ✓ Sidebar opened via parent.click()');
                return true;
            } catch (err) {
                console.warn('VocalBrand: Method 3 failed:', err);
            }
        }
        
        // Method 4: Search for ANY button that might open sidebar
        try {
            const allButtons = document.querySelectorAll('button');
            for (let btn of allButtons) {
                const ariaLabel = btn.getAttribute('aria-label') || '';
                const title = btn.getAttribute('title') || '';
                const classNames = btn.className || '';
                
                // Look for navigation-related buttons
                if (ariaLabel.includes('navigation') || 
                    ariaLabel.includes('menu') || 
                    ariaLabel.includes('sidebar') ||
                    title.includes('navigation') ||
                    title.includes('menu') ||
                    classNames.includes('sidebar')) {
                    btn.click();
                    console.log('VocalBrand: ✓ Sidebar opened via button search');
                    return true;
                }
            }
        } catch (err) {
            console.warn('VocalBrand: Method 4 failed:', err);
        }
        
        // Method 5: Directly manipulate sidebar CSS (Streamlit Cloud compatible)
        if (els.sidebar) {
            try {
                // Remove any negative transforms and force visible
                els.sidebar.style.cssText = `
                    transform: translateX(0) !important;
                    margin-left: 0 !important;
                    left: 0 !important;
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    /* Put the sidebar absolutely on top of everything */
                    z-index: 999999 !important; /* max int for safety */
                    position: fixed !important;
                    top: 0 !important;
                    height: 100vh !important;
                    width: 21rem !important;
                    max-width: 80vw !important;
                    background: white !important;
                    overflow-y: auto !important;
                    overflow-x: hidden !important;
                    box-shadow: 0 0 50px rgba(0,0,0,.3) !important;
                `;
                
                // Force all child elements visible
                const children = els.sidebar.querySelectorAll('*');
                children.forEach(child => {
                    child.style.visibility = 'visible';
                    child.style.opacity = '1';
                });
                
                // Also try setting attribute
                els.sidebar.setAttribute('data-sidebar-open', 'true');
                
                console.log('VocalBrand: ✓ Sidebar opened via CSS manipulation');
                return true;
            } catch (err) {
                console.warn('VocalBrand: Method 5 failed:', err);
            }
        }
        
        // Method 6: Trigger Streamlit's internal state (nuclear option)
        try {
            // Streamlit uses React under the hood - try to trigger state change
            if (window.streamlitDebug) {
                window.streamlitDebug.toggleSidebar();
                console.log('VocalBrand: ✓ Sidebar opened via Streamlit debug');
                return true;
            }
        } catch (err) {
            console.warn('VocalBrand: Method 6 failed:', err);
        }
        
        // Method 7: Create overlay that forces sidebar visible
        try {
            const sidebar = els.sidebar;
            if (sidebar) {
                // Force show with !important equivalent
                sidebar.style.cssText = `
                    transform: translateX(0) !important;
                    margin-left: 0 !important;
                    left: 0 !important;
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    z-index: 999999 !important;
                    position: fixed !important;
                    top: 0 !important;
                    height: 100vh !important;
                `;
                console.log('VocalBrand: ✓ Sidebar force-opened via cssText');
                return true;
            }
        } catch (err) {
            console.warn('VocalBrand: Method 7 failed:', err);
        }
        
        console.error('VocalBrand: ⚠️ All 7 methods failed - sidebar might already be open or Streamlit version incompatible');
        console.log('VocalBrand: Debug info:', {
            hamburger: !!els.hamburger,
            hamburgerBtn: !!els.hamburgerBtn,
            sidebar: !!els.sidebar,
            isMobile: isMobileView()
        });
        return false;
    }

    // Close sidebar by unchecking the CSS-only checkbox and resetting position
    function closeSidebar() {
        const toggle = document.getElementById('vb-nav-toggle');
        if (toggle) {
            toggle.checked = false;
        }
        
        // Also force sidebar off-screen via CSS as backup
        const sidebar = document.querySelector('[data-testid="stSidebar"]') || 
                       document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar && isMobileView()) {
            sidebar.style.transform = 'translateX(-100%)';
            sidebar.style.transition = 'transform 0.3s ease-in-out';
        }
    }
    
    // Force hamburger to be visible and properly styled
    function enforceHamburgerVisibility() {
        if (!isMobileView()) return;
        
        const els = getElements();
        
        if (els.hamburger) {
            // Apply critical styles to ensure visibility
            els.hamburger.style.position = 'fixed';
            els.hamburger.style.top = '1rem';
            els.hamburger.style.left = '1rem';
            els.hamburger.style.zIndex = '9999';
            els.hamburger.style.display = 'block';
            els.hamburger.style.visibility = 'visible';
            els.hamburger.style.opacity = '1';
        }
        
        if (els.hamburgerBtn) {
            els.hamburgerBtn.style.opacity = '1';
            els.hamburgerBtn.style.visibility = 'visible';
            els.hamburgerBtn.style.display = 'inline-flex';
            els.hamburgerBtn.style.width = '48px';
            els.hamburgerBtn.style.height = '48px';
        }
        
        // Ensure sidebar has proper z-index when opened
        if (els.sidebar) {
            els.sidebar.style.zIndex = '9998';
        }
    }
    
    // Sync FAB button visibility and overlay behavior
    function syncFab() {
        const els = getElements();
        if (!els.fab) return;
        
        if (isMobileView()) {
            els.fab.style.display = 'flex';
        } else {
            els.fab.style.display = 'none';
        }

        // Clicking overlay closes the menu (uncheck) - with multiple event types
        const overlay = document.getElementById('vb-nav-overlay');
        if (overlay && !overlay.dataset.bound) {
            // Use multiple event listeners for maximum compatibility
            overlay.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('VocalBrand: Overlay clicked - closing sidebar');
                closeSidebar();
            }, false);
            
            overlay.addEventListener('touchstart', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('VocalBrand: Overlay touched - closing sidebar');
                closeSidebar();
            }, { passive: false });
            
            overlay.dataset.bound = '1';
            console.log('VocalBrand: ✓ Overlay close handlers attached');
        }
    }
    
    // Main initialization
    function init() {
        const els = getElements();
        
        // Attach FAB click handler with ALL possible event types
        if (els.fab) {
            console.log('VocalBrand: Attaching FAB event listeners...');
            
            // Remove any existing listeners to prevent duplicates
            const newFab = els.fab.cloneNode(true);
            els.fab.parentNode.replaceChild(newFab, els.fab);
            
            // 1. Click event (standard)
            newFab.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('VocalBrand: FAB clicked (click event)');
                openSidebar(e);
            }, false);
            
            // 2. Touch events (iOS/Android)
            newFab.addEventListener('touchstart', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('VocalBrand: FAB touched (touchstart)');
                openSidebar(e);
            }, { passive: false });
            
            newFab.addEventListener('touchend', function(e) {
                e.preventDefault();
                console.log('VocalBrand: FAB touch ended');
            }, { passive: false });
            
            // 3. Pointer events (universal modern approach)
            newFab.addEventListener('pointerdown', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('VocalBrand: FAB pointer down (' + e.pointerType + ')');
                openSidebar(e);
            }, false);
            
            // 4. Mouse events (desktop fallback)
            newFab.addEventListener('mousedown', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('VocalBrand: FAB mouse down');
                openSidebar(e);
            }, false);
            
            // 5. Keyboard accessibility (Enter/Space)
            newFab.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    console.log('VocalBrand: FAB activated via keyboard');
                    openSidebar(e);
                }
            }, false);
            
            console.log('VocalBrand: ✓ FAB initialized with 5 event types');
        } else {
            console.warn('VocalBrand: FAB button not found!');
        }
        
        // Initial setup
        enforceHamburgerVisibility();
        syncFab();
        
        // CRITICAL: Force sidebar closed on mobile by default
        if (isMobileView()) {
            closeSidebar();
            console.log('VocalBrand: Sidebar forced closed on init');
        }
        
        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                enforceHamburgerVisibility();
                syncFab();
                // Close sidebar when resizing to avoid visual bugs
                if (isMobileView()) {
                    closeSidebar();
                }
            }, 200);
        });
        
        // Persistent monitoring to override any CSS that might hide elements
        // AND ensure sidebar is properly closed when checkbox is unchecked
        setInterval(function() {
            enforceHamburgerVisibility();
            syncFab();
            
            // CRITICAL: Ensure sidebar stays hidden when checkbox is unchecked
            if (isMobileView()) {
                const toggle = document.getElementById('vb-nav-toggle');
                const sidebar = document.querySelector('[data-testid="stSidebar"]') || 
                               document.querySelector('section[data-testid="stSidebar"]');
                
                if (toggle && !toggle.checked && sidebar) {
                    // Force sidebar off-screen if checkbox is unchecked
                    if (sidebar.style.transform !== 'translateX(-100%)') {
                        sidebar.style.transform = 'translateX(-100%)';
                        sidebar.style.transition = 'transform 0.3s ease-in-out';
                    }
                }
            }
        }, CHECK_INTERVAL);
        
        console.log('VocalBrand: Mobile navigation initialized ✓');
    }
    
    // Wait for DOM to be ready, then initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // AGGRESSIVE re-initialization for Streamlit Cloud (multiple attempts)
    setTimeout(init, 50);   // Very fast first retry
    setTimeout(init, 100);
    setTimeout(init, 250);
    setTimeout(init, 500);
    setTimeout(init, 1000);
    setTimeout(init, 1500);
    setTimeout(init, 2000);
    setTimeout(init, 3000); // Extra attempts for Streamlit Cloud
    setTimeout(init, 5000); // Final attempt
    
    console.log('VocalBrand: Scheduled 9 initialization attempts');
    
    // Add a visual indicator that FAB is ready (pulse animation)
    setTimeout(function() {
        const fab = document.getElementById('vb-fab-menu');
        if (fab && isMobileView()) {
            fab.classList.add('pulse');
            console.log('VocalBrand: FAB pulse animation added');
            // Remove pulse after 5 seconds
            setTimeout(function() {
                fab.classList.remove('pulse');
            }, 5000);
        }
    }, 1500);
})();

// ============================================================
// VOCALBRAND SUPREME DESKTOP SIDEBAR TOGGLE (single-source of truth)
// ============================================================
(function() {
    'use strict';

    // Sync legacy body class with new desktop checkbox so both CSS paths work
    try {
        const chk = document.getElementById('vb-desktop-chk');
        if (chk) {
            const sync = () => {
                document.body.classList.toggle('vb-sidebar-collapsed', chk.checked);
            };
            chk.addEventListener('change', sync);
            sync();
        }
    } catch {}

    const DESKTOP_MIN_WIDTH = 993;
    const SIDEBAR_SELECTOR = '[data-testid="stSidebar"], section[data-testid="stSidebar"]';
    const SIDEBAR_CANDIDATE_SELECTORS = [
        '[data-testid="stSidebar"]',
        'section[data-testid="stSidebar"]',
        'div[data-testid="stSidebar"]',
        '.stSidebar',
        '[class*="sidebar" i]',
        '[role="complementary"]'
    ];
    const COLLAPSED_CONTROL_SELECTOR = '[data-testid="collapsedControl"], div[data-testid="collapsedControl"]';
    // Support multiple Streamlit versions and themes
    const COLLAPSE_BUTTON_SELECTOR = [
        `${SIDEBAR_SELECTOR} button[kind="header"]`,
        `${SIDEBAR_SELECTOR} [data-testid*="baseButton"] button`,
        `${SIDEBAR_SELECTOR} button[aria-label*="collapse" i]`,
        `${SIDEBAR_SELECTOR} [aria-label*="close sidebar" i]`,
        `${SIDEBAR_SELECTOR} button[title*="collapse" i]`,
    ].join(',');
    const TOGGLE_BUTTON_ID = 'vb-desktop-toggle';
    const DESKTOP_ONLY_PROPS = [
        'position','top','left','transform','margin-left','width','min-width','max-width',
        'height','z-index','display','visibility','opacity','transition'
    ];
    const INLINE_PROPS = DESKTOP_ONLY_PROPS;

    let boundButton = null;

    console.log('VocalBrand SUPREME: Desktop toggle booting…');

    function isDesktop() {
        return window.innerWidth >= DESKTOP_MIN_WIDTH;
    }

    function getSidebar() {
        return document.querySelector(SIDEBAR_SELECTOR);
    }

    function getCollapsedControl() {
        return document.querySelector(COLLAPSED_CONTROL_SELECTOR);
    }

    function getSidebarCandidates() {
        const set = new Set();
        SIDEBAR_CANDIDATE_SELECTORS.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => set.add(el));
        });
        return Array.from(set).filter(Boolean);
    }

    function setSidebarStyles(styles) {
        const candidates = getSidebarCandidates();
        if (!candidates.length) return;
        candidates.forEach(sidebar => {
            Object.entries(styles).forEach(([prop, value]) => {
                if (value === null) sidebar.style.removeProperty(prop);
                else sidebar.style.setProperty(prop, value, 'important');
            });
            const shell = sidebar.parentElement;
            if (shell && shell instanceof HTMLElement) {
                Object.entries(styles).forEach(([prop, value]) => {
                    if (value === null) shell.style.removeProperty(prop);
                    else shell.style.setProperty(prop, value, 'important');
                });
            }
        });
    }

    function clearSidebarInlineStyles() {
        const candidates = getSidebarCandidates();
        candidates.forEach(sidebar => {
            INLINE_PROPS.forEach(p => {
                try { sidebar.style.removeProperty(p); } catch {}
            });
            const shell = sidebar.parentElement;
            if (shell && shell instanceof HTMLElement) {
                INLINE_PROPS.forEach(p => { try { shell.style.removeProperty(p); } catch {} });
            }
        });
        candidates.forEach(sidebar => {
            INLINE_PROPS.forEach(p => {
                try { sidebar.style.removeProperty(p); } catch {}
            });
            const shell = sidebar.parentElement;
            if (shell && shell instanceof HTMLElement) {
                INLINE_PROPS.forEach(p => { try { shell.style.removeProperty(p); } catch {} });
            }
        });
    }

    function resetDesktopForMobile() {
        const sidebar = getSidebar();
        if (!sidebar) return;
        DESKTOP_ONLY_PROPS.forEach(prop => sidebar.style.removeProperty(prop));
    }

    function detectCollapsed() {
        const sidebar = getSidebar();
        if (!sidebar) return false;

        const collapsedControl = getCollapsedControl();
        if (collapsedControl && collapsedControl.offsetParent !== null) return true;

        const computed = window.getComputedStyle(sidebar);
        if (computed.transform && computed.transform !== 'none') {
            const matrix = computed.transform;
            if (matrix.includes('-') && !matrix.includes('(1, 0, 0, 1, 0, 0)')) return true;
        }

        const rect = sidebar.getBoundingClientRect();
        if (rect.x <= -100 || rect.right <= 20 || rect.width < 40) return true;

        if (sidebar.style.transform && sidebar.style.transform.includes('translateX(-')) return true;

        return document.body.classList.contains('vb-sidebar-collapsed');
    }

    function syncExpandControl(collapsed) {
        const control = getCollapsedControl();
        if (!control) return;

        if (collapsed) {
            control.style.setProperty('display', 'block', 'important');
            control.style.setProperty('position', 'fixed', 'important');
            control.style.setProperty('left', '0', 'important');
            control.style.setProperty('top', '50%', 'important');
            control.style.setProperty('transform', 'translateY(-50%)', 'important');
            control.style.setProperty('z-index', '999999', 'important');
            const btn = control.querySelector('button');
            if (btn) {
                btn.style.setProperty('display', 'flex', 'important');
                btn.style.setProperty('visibility', 'visible', 'important');
                btn.style.setProperty('opacity', '1', 'important');
                btn.style.setProperty('pointer-events', 'auto', 'important');
            }
        } else {
            control.style.setProperty('display', 'none', 'important');
        }
    }

    function getSidebarWidth() {
        const sb = getSidebar();
        if (!sb) return 336; // default 21rem
        const computed = window.getComputedStyle(sb);
        const w = parseFloat(computed.width || '336');
        return isNaN(w) ? 336 : Math.max(240, Math.min(480, w));
    }

    function forceSidebarState(shouldBeOpen) {
        if (!isDesktop()) return;

        console.log('VocalBrand SUPREME: Forcing sidebar', shouldBeOpen ? 'OPEN' : 'CLOSED');
    const w = getSidebarWidth();
    // Sync CSS var used by CSS-only rules
    try { document.documentElement.style.setProperty('--vb-sidebar-w', `${w}px`); } catch {}

        if (shouldBeOpen) {
            setSidebarStyles({
                position: 'sticky',
                top: '0',
                left: '0',
                transform: 'translateX(0)',
                'margin-left': '0',
                width: `${w}px`,
                'min-width': `${w}px`,
                'max-width': `${w}px`,
                height: '100vh',
                'z-index': '1',
                display: 'block',
                visibility: 'visible',
                opacity: '1',
                transition: 'transform 0.3s ease-in-out'
            });
        } else {
            setSidebarStyles({
                position: 'fixed',
                top: '0',
                left: '0',
                // Use both pixel-based and percentage-based transforms as belt-and-suspenders
                transform: `translateX(-${w}px)`,
                width: `${w}px`,
                'min-width': `${w}px`,
                'max-width': `${w}px`,
                height: '100vh',
                'z-index': '9999',
                display: 'block',
                visibility: 'visible',
                opacity: '1',
                transition: 'transform 0.3s ease-in-out'
            });
            // Also set style attribute using percentage on all candidates
            getSidebarCandidates().forEach(el => {
                try {
                    el.style.setProperty('transform', 'translateX(-100%)', 'important');
                    el.style.setProperty('pointer-events', 'none', 'important');
                    el.style.setProperty('visibility', 'hidden', 'important');
                    el.style.setProperty('opacity', '0.9999', 'important'); // keep layout stable but hidden
                } catch {}
            });
        }

        syncExpandControl(!shouldBeOpen);
        document.body.classList.toggle('vb-sidebar-collapsed', !shouldBeOpen);
    }

    function updateButtonState() {
        const btn = document.getElementById(TOGGLE_BUTTON_ID);
        if (!btn) {
            boundButton = null;
            return;
        }

        if (!isDesktop()) {
            btn.style.setProperty('display', 'none', 'important');
            // Do not mutate body class here; mobile logic owns sidebar.
            resetDesktopForMobile();
            return;
        }

        // Prefer our body class as the single source of truth; fall back to detection
        const collapsed = document.body.classList.contains('vb-sidebar-collapsed') || detectCollapsed();
        const glyph = collapsed ? '\u00BB' : '\u00AB';
        btn.textContent = glyph;
        btn.setAttribute('aria-expanded', String(!collapsed));
        btn.style.setProperty('display', 'flex', 'important');
        syncExpandControl(collapsed);

        if (collapsed) {
            setSidebarStyles({ display: 'block', visibility: 'visible', opacity: '1' });
        }
    }

    function rebindButton() {
        const btn = document.getElementById(TOGGLE_BUTTON_ID);
        if (!btn) {
            boundButton = null;
            return;
        }

        if (boundButton === btn) return;

        if (boundButton) {
            boundButton.removeEventListener('click', handleToggleClick, true);
            boundButton.removeEventListener('click', handleToggleClick, false);
        }
        // Bind multiple event types for maximum reliability
        btn.addEventListener('click', handleToggleClick, false);
        btn.addEventListener('pointerdown', handleToggleClick, false);
        btn.addEventListener('mousedown', handleToggleClick, false);
        btn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                handleToggleClick(e);
            }
        }, false);
        btn.dataset.vbSupremeBound = '1';
        boundButton = btn;
        console.log('VocalBrand SUPREME: Toggle wired to', btn);
    }

    function handleToggleClick(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        if (!isDesktop()) {
            updateButtonState();
            return;
        }

        const collapsedBefore = document.body.classList.contains('vb-sidebar-collapsed') || detectCollapsed();
        console.log('VocalBrand SUPREME: Toggle clicked. collapsedBefore =', collapsedBefore);

    // First, flip our CSS-driven state immediately for instant UX
        const shouldBeOpen = collapsedBefore; // if it was collapsed, we want open
        document.body.classList.toggle('vb-sidebar-collapsed', !shouldBeOpen);
    // Clear any inline overrides so CSS rules take effect cleanly
    clearSidebarInlineStyles();

        // Then, try to sync with Streamlit native state (best-effort)
        if (collapsedBefore) {
            const expandBtn = document.querySelector(`${COLLAPSED_CONTROL_SELECTOR} button, [aria-label*="expand sidebar" i], [title*="expand" i]`);
            if (expandBtn) {
                try { expandBtn.click(); } catch (err) { console.warn('VocalBrand SUPREME: Native expand failed', err); }
            }
        } else {
            let collapseBtn = document.querySelector(COLLAPSE_BUTTON_SELECTOR);
            if (!collapseBtn) {
                collapseBtn = document.querySelector('[aria-label*="collapse" i], [title*="collapse" i]');
            }
            if (collapseBtn) {
                try { collapseBtn.click(); } catch (err) { console.warn('VocalBrand SUPREME: Native collapse failed', err); }
            }
        }

        // As a fallback only, if CSS didn't win yet, nudge after a moment
        setTimeout(() => forceSidebarState(shouldBeOpen), 160);
        setTimeout(updateButtonState, 40);
        setTimeout(updateButtonState, 180);
        setTimeout(updateButtonState, 400);
    }

    function heartbeat() {
        rebindButton();
        updateButtonState();
    }

    function init() {
        // Expose global immediately so inline onclick can call it
        try { window.vbToggleSidebar = () => handleToggleClick(); } catch {}
        heartbeat();
        console.log('VocalBrand SUPREME: Desktop toggle initialized.');
        // Re-set global helper after heartbeat (safety)
        try { window.vbToggleSidebar = () => handleToggleClick(); } catch {}
        // Delegated fallback: capture clicks anywhere on the button
        document.addEventListener('click', (e) => {
            const t = e.target;
            if (t && (t.id === TOGGLE_BUTTON_ID || (t.closest && t.closest('#'+TOGGLE_BUTTON_ID)))) {
                handleToggleClick(e);
            }
        }, true);
        // Nuclear CSS-only override as a last resort
        try {
            const css = `@media (min-width: ${DESKTOP_MIN_WIDTH}px){
                body.vb-sidebar-collapsed [data-testid="stSidebar"],
                body.vb-sidebar-collapsed section[data-testid="stSidebar"],
                body.vb-sidebar-collapsed div[data-testid="stSidebar"],
                body.vb-sidebar-collapsed .stSidebar,
                body.vb-sidebar-collapsed [class*="sidebar" i]{
                    transform: translateX(-100%) !important;
                    opacity: 0.0001 !important;
                    pointer-events: none !important;
                    visibility: hidden !important;
                    position: fixed !important;
                    left: 0 !important; top: 0 !important; height: 100vh !important;
                }
                body:not(.vb-sidebar-collapsed) [data-testid="stSidebar"],
                body:not(.vb-sidebar-collapsed) section[data-testid="stSidebar"],
                body:not(.vb-sidebar-collapsed) div[data-testid="stSidebar"],
                body:not(.vb-sidebar-collapsed) .stSidebar,
                body:not(.vb-sidebar-collapsed) [class*="sidebar" i]{
                    transform: translateX(0) !important;
                    opacity: 1 !important;
                    pointer-events: all !important;
                    visibility: visible !important;
                }
            }`;
            const styleEl = document.createElement('style');
            styleEl.textContent = css;
            document.head.appendChild(styleEl);
        } catch {}
    }

    init();
    setTimeout(heartbeat, 80);
    setTimeout(heartbeat, 200);
    setTimeout(heartbeat, 500);
    setTimeout(heartbeat, 1000);
    setTimeout(heartbeat, 2000);

    window.addEventListener('resize', () => {
        setTimeout(heartbeat, 60);
    });

    const observer = new MutationObserver(() => {
        setTimeout(heartbeat, 50);
    });
    observer.observe(document.body, { childList: true, subtree: true });

    setInterval(heartbeat, 700);
})();
</script>
    """
    # Prefer st.html (Streamlit >= 1.36) which allows scripts in the main DOM
    try:
        html_func = getattr(st, "html", None)
        if callable(html_func):
            html_func(html)
        else:
            st.markdown(html, unsafe_allow_html=True)
    except Exception:
        # Fallback to markdown if html is unavailable
        st.markdown(html, unsafe_allow_html=True)


def inject_supreme_sidebar_and_audio_fix():
        """Additive-only CSS/JS to:
        1) Align sidebar divider with the desktop toggle seam.
        2) Keep all Navigation radios visible, single-line, perfectly aligned.
        3) Ensure Pro Recorder audio player appears after recording.
        """
        import streamlit as st
        html = """
        <style>
            /* ---------- 1) Sidebar + global seam line (aligned with toggle) ---------- */
            section[data-testid="stSidebar"]{
                position: relative !important;
                overflow-y: auto !important;
                max-height: 100vh !important;
            }
            /* Disable any prior pseudo-dividers to avoid double-lines */
            section[data-testid="stSidebar"]::before,
            [data-testid="stSidebar"]::before{
                content: "" !important;
                position: absolute !important;
                top: 0 !important;
                bottom: 0 !important;
                left: calc(
                    var(--vb-sidebar-w, 336px) - var(--vb-toggle-overlap, 8px) - 3px
                ) !important;
                width: 3px !important;
                display: block !important;
                border-radius: 0 999px 999px 0 !important;
                background: linear-gradient(180deg,
                    rgba(12, 30, 66, 0.98) 0%,
                    rgba(19, 49, 96, 0.98) 34%,
                    rgba(28, 76, 140, 0.96) 68%,
                    rgba(30, 100, 160, 0.94) 100%
                ) !important;
                border-left: 1px solid rgba(8, 22, 48, 0.65) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.45) !important;
                box-shadow:
                    0 0 0 1px rgba(11, 27, 60, 0.35) !important,
                    0 6px 28px rgba(15, 23, 42, 0.32) !important;
                opacity: 0 !important;
                transform: none !important;
                transition: opacity 0.28s ease, transform 0.28s ease !important;
                pointer-events: none !important;
            }

            section[data-testid="stSidebar"]::after,
            [data-testid="stSidebar"]::after{
                content: "" !important;
                position: absolute !important;
                top: -6px !important;
                bottom: -6px !important;
                left: calc(
                    var(--vb-sidebar-w, 336px) - var(--vb-toggle-overlap, 8px) - 6px
                ) !important;
                width: 9px !important;
                border-radius: 999px !important;
                background: linear-gradient(180deg,
                    rgba(48, 86, 140, 0.42) 0%,
                    rgba(32, 102, 180, 0.32) 55%,
                    rgba(16, 185, 129, 0.25) 100%
                ) !important;
                filter: blur(6px) !important;
                opacity: 0 !important;
                transition: opacity 0.35s ease !important;
                pointer-events: none !important;
            }

            @media (min-width: 993px) {
                body:not(.vb-sidebar-collapsed) section[data-testid="stSidebar"]::before,
                body:not(.vb-sidebar-collapsed) [data-testid="stSidebar"]::before{
                    opacity: 1 !important;
                    transform: none !important;
                }
                body:not(.vb-sidebar-collapsed) section[data-testid="stSidebar"]::after,
                body:not(.vb-sidebar-collapsed) [data-testid="stSidebar"]::after{
                    opacity: 1 !important;
                }
            }

            @media (max-width: 992px) {
                body:has(#vb-nav-toggle:checked) section[data-testid="stSidebar"]::before,
                body:has(#vb-nav-toggle:checked) [data-testid="stSidebar"]::before{
                    opacity: 1 !important;
                    transform: none !important;
                    left: 0 !important;
                }
                body:has(#vb-nav-toggle:checked) section[data-testid="stSidebar"]::after,
                body:has(#vb-nav-toggle:checked) [data-testid="stSidebar"]::after{
                    opacity: 0.85 !important;
                    left: -2px !important;
                }
            }

            /* Seam line as a fixed overlay that aligns to the toggle's seam */
            @media (min-width: 993px) {
                .vb-seam-line {
                    position: fixed !important;
                    top: 0 !important;
                    bottom: 0 !important;
                    width: 1px !important;
                    background: rgba(15, 23, 42, 0.12) !important;
                    pointer-events: none !important;
                    z-index: 99998 !important; /* just below toggle */
                }
                :root:not(:has(#vb-desktop-chk:checked)) .vb-seam-line { left: var(--vb-sidebar-w, 336px) !important; }
                :root:has(#vb-desktop-chk:checked) .vb-seam-line { left: 0 !important; }

                /* Green content rail: subtle accent line in content area */
                .vb-rail-green {
                    position: fixed !important;
                    top: 0 !important;
                    bottom: 0 !important;
                    width: 3px !important;
                    background: linear-gradient(180deg, var(--success-green), #22c55e) !important;
                    pointer-events: none !important;
                    z-index: 99997 !important; /* below seam/toggle */
                    border-radius: 2px !important;
                    opacity: 0.9 !important;
                }
                /* When sidebar open, rail sits slightly inside content area */
                :root:not(:has(#vb-desktop-chk:checked)) .vb-rail-green { left: calc(var(--vb-sidebar-w, 336px) + 16px) !important; }
                /* When sidebar closed, keep it near the left app edge */
                :root:has(#vb-desktop-chk:checked) .vb-rail-green { left: 16px !important; }
            }
            @media (max-width: 992px) { .vb-seam-line, .vb-rail-green { display: none !important; } }

            /* ---------- 2) Navigation radios: gentle alignment (preserve layout) ---------- */
            /* Keep existing look; only normalize spacing for consistent circle column */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"]{
                margin: 0.25rem 0 !important;
            }
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label{
                display: flex !important;
                align-items: center !important;
                gap: 0.5rem !important;
                padding: 0.375rem 0.875rem !important;
                margin: 0.125rem 0 !important;
                white-space: nowrap !important;
                writing-mode: horizontal-tb !important;
                text-orientation: mixed !important;
            }
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label input[type="radio"]{
                width: 18px !important;
                height: 18px !important;
                flex: 0 0 auto !important;
                margin: 0 0.625rem 0 0 !important; /* fixed space before text */
            }
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label span,
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label div{
                display: inline-flex !important;
                align-items: center !important;
                min-width: 0 !important;
            }

            /* Selected state: premium highlight without offsetting alignment */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label[aria-checked="true"]{
                background: linear-gradient(180deg, rgba(30,58,138,0.06), rgba(30,58,138,0.03)) !important;
                box-shadow: 0 2px 8px rgba(2,6,23,0.06) !important;
            }

            /* Ensure the whole nav block fits; if not, sidebar scrolls (see container rule above) */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"]{
                margin-bottom: 0.5rem !important;
            }

            /* ---------- 3) Pro Recorder: guarantee audio player visibility after recording ---------- */
            /* Unhide/size Streamlit audio container across themes */
                    [data-testid="stAudio"],
                    [data-testid="stAudio"] audio,
                    [data-testid="stAudioPlayer"],
                    [data-testid="stAudioPlayer"] audio{
                display: block !important;
                width: 100% !important;
                min-height: 44px !important;       /* visible, tappable */
                opacity: 1 !important;
                visibility: visible !important;
            }
            /* Prevent clipping by parent containers */
                    [data-testid="stAudio"],
                    [data-testid="stAudioPlayer"]{
                overflow: visible !important;
                margin-top: 0.5rem !important;
                margin-bottom: 0.75rem !important;
                z-index: 2;
            }

            /* Subtle info chip near recorders (non-invasive) */
            .vb-recorder-note{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: 12.5px;
                color: #334155;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 999px;
                padding: 6px 10px;
                margin: 6px 0 2px 0;
            }
            .vb-recorder-note b{ color:#1e3a8a; }
        </style>

        <script>
        (function(){
            'use strict';

            // 🎯 PART 1: GLOBAL SEAM OVERLAY (aligned to toggle via CSS var)
            // Create once and anchor to viewport using --vb-sidebar-w
            (function ensureSeam(){
                if (document.querySelector('.vb-seam-line')) return;
                const seam = document.createElement('div');
                seam.className = 'vb-seam-line';
                document.body.appendChild(seam);
                console.log('[VB] ✅ Seam overlay created');
            })();

            // 🎯 PART 1b: GREEN CONTENT RAIL (visual accent in content area)
            (function ensureGreenRail(){
                if (document.querySelector('.vb-rail-green')) return;
                const rail = document.createElement('div');
                rail.className = 'vb-rail-green';
                document.body.appendChild(rail);
                console.log('[VB] ✅ Green rail created');
            })();

            // 🎯 PART 2: No JS needed for radios (CSS-only gentle alignment above)

            // 🎯 PART 3: MOBILE PRO RECORDER FIX (audio player injection)

            let capturedBlob = null;
            let capturedBlobURL = null;

            // 3a) Force-reveal any Streamlit audio players (belt & suspenders)
            const once = new Set();
            const revealAudio = (node) => {
                if (!node || once.has(node)) return;
                once.add(node);
                try{
                    node.style.display = 'block';
                    node.style.opacity = '1';
                    node.style.visibility = 'visible';
                    const audio = node.querySelector('audio');
                    if (audio){
                        audio.controls = true;
                        setTimeout(() => {
                            node.scrollIntoView({behavior:'smooth', block:'nearest', inline:'nearest'});
                        }, 120);
                    }
                    console.log('[VB] ✅ Revealed Streamlit audio player');
                }catch(e){}
            };

            const mo = new MutationObserver((mList) => {
                for(const m of mList){
                    m.addedNodes && m.addedNodes.forEach(n => {
                        if (!(n instanceof HTMLElement)) return;
                        if (n.matches?.('[data-testid="stAudio"], [data-testid="stAudioPlayer"]')) revealAudio(n);
                        const maybe = n.querySelector?.('[data-testid="stAudio"], [data-testid="stAudioPlayer"]');
                        if (maybe) revealAudio(maybe);
                    });
                }
            });

            if (document.body){
                mo.observe(document.body, {childList:true, subtree:true});
            }

            // 3b) NUCLEAR: Inject manual player when Streamlit fails
            function findRecorderContainer(){
                const candidates = Array.from(document.querySelectorAll('div, section, [data-testid]'));
                return candidates.find(el => {
                    const text = (el.textContent || '').toLowerCase();
                    return (text.includes('captured') && text.includes('kb')) || 
                           text.includes('pro recorder') ||
                           el.querySelector('canvas');
                });
            }

            function injectManualAudioPlayer(audioBlob){
                if (!audioBlob) return;
                console.log('[VB] 🎯 Injecting manual audio player, blob size:', audioBlob.size);
                
                const container = findRecorderContainer();
                if (!container) {
                    console.warn('[VB] Could not find recorder container');
                    return;
                }

                if (document.getElementById('vb-manual-audio-player')) {
                    console.log('[VB] Player already exists, updating');
                    const existing = document.getElementById('vb-manual-audio-player');
                    const existingAudio = existing.querySelector('audio');
                    if (existingAudio && audioBlob) {
                        const newURL = URL.createObjectURL(audioBlob);
                        existingAudio.src = newURL;
                        existingAudio.load();
                    }
                    return;
                }

                const audioURL = URL.createObjectURL(audioBlob);
                capturedBlobURL = audioURL;

                const playerDiv = document.createElement('div');
                playerDiv.id = 'vb-manual-audio-player';
                playerDiv.style.cssText = 'margin:1rem 0;padding:1rem;background:#f8fafc;border:2px solid #1a365d;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);';

                playerDiv.innerHTML = '<div style="font-weight:700;color:#1a365d;margin-bottom:0.5rem;font-size:14px;">✅ Recording Complete</div><audio controls style="width:100%;margin-bottom:0.75rem;border-radius:8px;"><source src="' + audioURL + '" type="audio/wav"><source src="' + audioURL + '" type="audio/webm"><source src="' + audioURL + '" type="audio/mp4">Your browser does not support audio playback.</audio><button id="vb-download-recording" style="width:100%;padding:0.75rem;background:linear-gradient(135deg,#1a365d 0%,#2563eb 100%);color:white;border:none;border-radius:10px;font-weight:700;font-size:16px;cursor:pointer;box-shadow:0 4px 8px rgba(0,0,0,0.15);">⬇️ Download Recording</button>';

                const waveform = container.querySelector('canvas');
                if (waveform && waveform.parentNode) {
                    waveform.parentNode.insertBefore(playerDiv, waveform.nextSibling);
                } else {
                    container.appendChild(playerDiv);
                }

                setTimeout(() => { playerDiv.scrollIntoView({behavior:'smooth',block:'center'}); }, 150);

                const downloadBtn = document.getElementById('vb-download-recording');
                if (downloadBtn) {
                    downloadBtn.addEventListener('click', function(){
                        try {
                            const a = document.createElement('a');
                            a.href = audioURL;
                            a.download = 'vocalbrand-recording-' + Date.now() + '.wav';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            downloadBtn.textContent = '✅ Downloaded!';
                            downloadBtn.style.background = '#10b981';
                            setTimeout(() => {
                                downloadBtn.textContent = '⬇️ Download Recording';
                                downloadBtn.style.background = 'linear-gradient(135deg,#1a365d 0%,#2563eb 100%)';
                            }, 2000);
                        } catch(err) {
                            console.error('[VB] Download failed:', err);
                            alert('Download failed. Try a different browser.');
                        }
                    });
                }

                console.log('[VB] ✅ Manual player injected');
            }

            // 3c) Intercept MediaRecorder to capture blob
            if (window.MediaRecorder && !window.MediaRecorder.__vbPatched) {
                const OriginalMR = window.MediaRecorder;
                window.MediaRecorder = function(...args) {
                    const recorder = new OriginalMR(...args);
                    const origStop = recorder.stop.bind(recorder);
                    const origOnData = recorder.ondataavailable;
                    
                    recorder.ondataavailable = function(event) {
                        if (event.data && event.data.size > 0) {
                            console.log('[VB] Captured blob:', event.data.size, 'bytes');
                            capturedBlob = event.data;
                            setTimeout(() => { if (capturedBlob) injectManualAudioPlayer(capturedBlob); }, 800);
                        }
                        if (origOnData) origOnData.call(recorder, event);
                    };
                    
                    recorder.stop = function() {
                        console.log('[VB] MediaRecorder.stop() intercepted');
                        return origStop();
                    };
                    
                    return recorder;
                };
                Object.setPrototypeOf(window.MediaRecorder, OriginalMR);
                Object.setPrototypeOf(window.MediaRecorder.prototype, OriginalMR.prototype);
                window.MediaRecorder.__vbPatched = true;
                console.log('[VB] ✅ MediaRecorder patched');
            }

            // 3d) Monitor Stop button clicks
            document.addEventListener('click', function(e){
                const target = e.target;
                if (!target) return;
                const text = (target.textContent || '').trim().toLowerCase();
                if (text === 'stop' || text.includes('stop recording')) {
                    console.log('[VB] Stop clicked, waiting for blob...');
                    let attempts = 0;
                    const pollInterval = setInterval(() => {
                        attempts++;
                        if (capturedBlob) {
                            clearInterval(pollInterval);
                            injectManualAudioPlayer(capturedBlob);
                        } else if (attempts > 20) {
                            clearInterval(pollInterval);
                            console.warn('[VB] No blob after 10s');
                        }
                    }, 500);
                }
            }, true);

            // 3e) Guidance note
            function placeRecorderNote(){
                const texts = ['Record','Recorder','Start recording','Pro Recorder'];
                const candidates = Array.from(document.querySelectorAll('button,[role="button"],h3,h4,label,p'))
                    .filter(el => texts.some(t => (el.textContent || '').toLowerCase().includes(t.toLowerCase())));
                if (!candidates.length) return;
                const anchor = candidates[0];
                if (anchor && !document.querySelector('.vb-recorder-note')){
                    const chip = document.createElement('div');
                    chip.className = 'vb-recorder-note';
                    chip.innerHTML = '💡 <b>Mobile:</b> Audio player appears below after recording with play + download.';
                    anchor.parentNode?.insertBefore(chip, anchor.nextSibling);
                }
            }

            if (document.readyState === 'loading'){
                document.addEventListener('DOMContentLoaded', placeRecorderNote);
            } else {
                placeRecorderNote();
            }

            console.log('[VB] 🎯 Supreme Mobile Pro Recorder Fix loaded');
        })();
        </script>
        """
        st.markdown(html, unsafe_allow_html=True)


def inject_tiktok_browser_fix():
    """Detect TikTok in-app browser and warn users about microphone limitations.
    
    TikTok's WebView blocks navigator.mediaDevices.getUserMedia even with permissions.
    This function detects TikTok browser and provides "Open in Browser" solution.
    
    Features:
    - Detects TikTok/musical_ly user agents (iOS & Android)
    - Shows prominent warning with VocalBrand branding
    - Provides "Open in Browser" button + manual instructions
    - Includes iOS and Android specific guidance
    - Logs technical details to console for debugging
    - Zero impact on non-TikTok browsers (graceful degradation)
    - Session storage to avoid nagging users repeatedly
    """
    html = """
    <!-- ULTRA SUPREME TikTok guardrail (instant write for early visibility) -->
    <script>
    (function(){
      'use strict';
      const ua = (navigator.userAgent||'') + ' ' + (navigator.vendor||'');
      const ref = document.referrer || '';
      const loc = window.location.href || '';
      const tokenMatch = /(TikTok|TTWebView|Bytedance|BytedanceWebview|Aweme|musical_ly|trill|\bTT\d+\b)/i.test(ua);
      const shimMatch  = /tiktok\.com\/link\/v2/i.test(loc) || /tiktok\.com/i.test(ref);
      const guessWebView = /\bwv\b/i.test(ua) || ((/CPU iPhone OS|iPad|iPhone/.test(ua)) && !/Safari/i.test(ua));
      const IS_TIKTOK = !!(tokenMatch || shimMatch);
      if (IS_TIKTOK) window.VB_IS_TIKTOK = true;
      if (IS_TIKTOK) {
        try {
          document.write('<style>#vb-tiktok-warning{display:flex!important;visibility:visible!important;opacity:1!important;}</style>');
          document.write('<style>body{overflow:hidden!important;}</style>');
        } catch {}
      }
    })();
    </script>

    <div id="vb-tiktok-warning" style="display:none;">
      <div id="vb-tiktok-content" style="max-width:520px;width:100%;background:#fff;border-radius:16px;padding:24px;box-shadow:0 20px 60px rgba(0,0,0,.3);text-align:center;">
        <div style="font-size:48px;margin-bottom:8px;">🎤</div>
        <h2 style="margin:.25rem 0 1rem 0;color:#1a365d;font-weight:800;">Recording Not Available in TikTok</h2>
        <p style="line-height:1.6;color:#0f172a;margin:0 0 16px 0;">
          TikTok's in‑app browser blocks microphone access. To record, open this page in your device browser.
        </p>
        <button id="vb-tiktok-open-btn" style="background:linear-gradient(135deg,#1a365d 0%,#2563eb 100%);color:#fff;border:none;border-radius:12px;padding:14px 18px;font-weight:700;width:100%;max-width:340px;margin:0 auto 10px;display:block;">
          🌐 Open in Safari/Chrome
        </button>
        <button id="vb-tiktok-use-pro" style="background:#fff;color:#1a365d;border:2px solid #1a365d;border-radius:12px;padding:12px 16px;font-weight:700;width:100%;max-width:340px;margin:0 auto 12px;display:block;">
          🎧 Try Pro Recorder (advanced)
        </button>
        <details style="text-align:left;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px;">
          <summary style="cursor:pointer;font-weight:700;color:#1a365d;">Manual steps (if the button doesn’t open)</summary>
          <div style="padding:10px 6px 0;color:#0f172a;">
            <p><strong>iPhone/iPad:</strong> Tap the three dots (•••) → “Open in Safari”.</p>
            <p><strong>Android:</strong> Tap the three dots (⋮) → “Open in browser/Chrome”.</p>
          </div>
        </details>
        <button id="vb-tiktok-dismiss-btn" style="background:#fff;color:#64748b;border:2px solid #e2e8f0;border-radius:10px;padding:10px 14px;font-weight:600;width:100%;max-width:340px;margin:10px auto 0;">
          I’ll browse without recording
        </button>
      </div>
    </div>

    <style>
      #vb-tiktok-warning{position:fixed;inset:0;background:rgba(0,0,0,.85);backdrop-filter:blur(8px);z-index:2147483647;display:none;align-items:center;justify-content:center;padding:16px;}
      #vb-tiktok-warning.vb-show{display:flex!important;}
      @keyframes vbPulse{0%,100%{transform:scale(1);}50%{transform:scale(1.04);}}
      #vb-tiktok-content .pulse{animation:vbPulse 2s ease-in-out infinite;}
      .vb-highlight-pulse{outline:3px solid #1a365d;outline-offset:2px;border-radius:12px;box-shadow:0 0 0 0 rgba(26,54,93,.45);animation:vbPulseOutline 1.5s ease-out 0s 2;}
      @keyframes vbPulseOutline{0%{box-shadow:0 0 0 0 rgba(26,54,93,.45);}70%{box-shadow:0 0 0 12px rgba(26,54,93,0);}100%{box-shadow:0 0 0 0 rgba(26,54,93,0);}}
      .vb-tiktok-inline-hint{display:none;}
      body.vb-tiktok .vb-tiktok-inline-hint{display:flex;gap:.75rem;background:#fff7ed;border:1px solid #f59e0b;color:#78350f;border-radius:12px;padding:.75rem 1rem;margin:.5rem 0 1rem;align-items:flex-start;}
      .vb-tiktok-inline-hint .actions{display:flex;gap:.5rem;flex-wrap:wrap;}
      .vb-tiktok-inline-hint .btn{border-radius:10px;padding:.5rem .9rem;font-weight:700;border:2px solid #1a365d;color:#1a365d;background:#fff;cursor:pointer;}
      .vb-tiktok-inline-hint .btn.primary{background:#1a365d;color:#fff;}
      .vb-tiktok-inline-hint .dismiss{margin-left:auto;background:transparent;border:none;color:#78350f;font-weight:800;cursor:pointer;}
    </style>

    <script>
    (function(){
      'use strict';
      const ua = (navigator.userAgent||'') + ' ' + (navigator.vendor||'');
      const ref = document.referrer || '';
      const loc = window.location.href || '';
      const tokenMatch = /(TikTok|TTWebView|Bytedance|BytedanceWebview|Aweme|musical_ly|trill|\bTT\d+\b)/i.test(ua);
      const shimMatch  = /tiktok\.com\/link\/v2/i.test(loc) || /tiktok\.com/i.test(ref);
      const guessWebView = /\bwv\b/i.test(ua) || ((/CPU iPhone OS|iPad|iPhone/.test(ua)) && !/Safari/i.test(ua));
      const IS_TIKTOK = !!(window.VB_IS_TIKTOK || tokenMatch || shimMatch);

            // Client-only analytics helpers (no network). Stores simple counters.
            function anaBump(key, oncePerSession){
                try {
                    if (oncePerSession) {
                        const sk = 'vb_ana_once_'+key;
                        if (sessionStorage.getItem(sk)==='1') return;
                        sessionStorage.setItem(sk,'1');
                    }
                    const n = parseInt(localStorage.getItem(key) || '0', 10) || 0;
                    localStorage.setItem(key, String(n+1));
                } catch {}
            }

      if (IS_TIKTOK) { try{ document.body.classList.add('vb-tiktok'); }catch{} }
            if (IS_TIKTOK) { anaBump('vb_ana_tiktok_hits', true); }

      function showModal() {
        const el = document.getElementById('vb-tiktok-warning');
        if (!el) return;
        el.classList.add('vb-show');
        try{ document.body.style.overflow='hidden'; }catch{}
      }
      function hideModal() {
        const el = document.getElementById('vb-tiktok-warning');
        if (!el) return;
        el.classList.remove('vb-show');
        try{ document.body.style.overflow=''; }catch{}
      }

      function openExtern() {
        const url = window.location.href.replace(/https?:\/\/www\./,'https://');
        let ok = false;
        try{ const w = window.open(url,'_blank'); if (w) ok = true; }catch{}
        if (!ok) {
          try{
            const a = document.createElement('a');
            a.href = url; a.target = '_blank'; a.rel='noopener noreferrer';
            document.body.appendChild(a); a.click(); a.remove(); ok = true;
          }catch{}
        }
        if (!ok && /Android/i.test(ua)) {
          try { window.location.href = 'intent://' + url.replace(/^https?:\/\//,'') + '#Intent;scheme=https;package=com.android.chrome;end'; ok = true; } catch {}
        }
        if (!ok) { try{ window.location.href = url; ok = true; }catch{} }
                anaBump('vb_ana_open_clicks');
        return ok;
      }

      function findPro() {
        const nodes = Array.from(document.querySelectorAll('button,a,[role="button"],[data-testid]'));
        return nodes.find(n => /Pro\s*Recorder|Recording\s*\(Pro\)|Advanced\s*Recorder|Studio\s*Recorder/i.test(n.innerText||'')) ||
               nodes.find(n => /pro/i.test(n.innerText||'') && /record/i.test(n.innerText||''));
      }
      function goPro() {
        const el = findPro();
        if (!el) return false;
        try{ el.scrollIntoView({behavior:'smooth',block:'center'}); }catch{ el.scrollIntoView(); }
        try{ el.classList.add('vb-highlight-pulse'); setTimeout(()=>el.classList.remove('vb-highlight-pulse'), 3500);}catch{}
        hideModal();
                anaBump('vb_ana_pro_clicks');
        return true;
      }

      function placeInlineHint() {
        if (!(IS_TIKTOK || window.VB_IS_TIKTOK)) return;
        if (document.getElementById('vb-tiktok-hint')) return;
        try { if (sessionStorage.getItem('vb-tiktok-hint-dismissed')==='true') return; } catch {}
        const blocks = Array.from(document.querySelectorAll('[data-testid], .element-container, section, div, main'));
        const target = blocks.find(b => /start recording|record a 30-60s sample|record a sample|microphone/i.test((b.innerText||'').toLowerCase()));
        if (!target) return;
        const d = document.createElement('div');
        d.id = 'vb-tiktok-hint';
        d.className = 'vb-tiktok-inline-hint';
        d.innerHTML = '<div style="font-size:22px;line-height:1;">🔒</div><div><div style="font-weight:800;color:#1a365d;">TikTok limits microphone access here</div><div style="font-weight:600;">Open in your device browser to record, or try the Pro Recorder below.</div><div class="actions"><button class="btn primary" data-act="open">Open in Browser</button><button class="btn" data-act="pro">Try Pro Recorder</button></div></div><button class="dismiss" title="Dismiss" aria-label="Dismiss" data-act="dismiss">×</button>';
        d.addEventListener('click', (e)=>{
          const a = e.target && e.target.closest ? e.target.closest('[data-act]') : null;
          if (!a) return;
          const act = a.getAttribute('data-act');
          if (act==='open') openExtern();
          if (act==='pro') goPro();
          if (act==='dismiss') { try{ sessionStorage.setItem('vb-tiktok-hint-dismissed','true'); }catch{} d.remove(); }
        }, {capture:true});
        try { target.prepend(d); } catch { target.insertBefore(d, target.firstChild); }
      }

      function interceptGUM() {
        if (!(IS_TIKTOK || window.VB_IS_TIKTOK)) return;
        if (!navigator.mediaDevices) return;
        if (navigator.mediaDevices.__vbPatched) return;
        const orig = navigator.mediaDevices.getUserMedia ? navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices) : null;
        navigator.mediaDevices.__vbOriginalGetUserMedia = orig;
        navigator.mediaDevices.getUserMedia = function() {
          showModal();
                    anaBump('vb_ana_gum_intercepts');
          return Promise.reject(new DOMException('Microphone blocked in TikTok in-app browser. Open externally or try Pro Recorder.', 'NotAllowedError'));
        };
        ['getUserMedia','webkitGetUserMedia','mozGetUserMedia'].forEach(k=>{ try { if (navigator[k]) navigator[k] = function(){ showModal(); }; } catch {} });
        navigator.mediaDevices.__vbPatched = true;
      }

      function interceptRecordClicks() {
        if (!(IS_TIKTOK || window.VB_IS_TIKTOK)) return;
        const handler = (e)=>{
          const t = e.target && e.target.closest ? e.target.closest('button,a,[role="button"],[data-testid]') : e.target;
          if (!t) return;
          const label = (t.innerText || t.getAttribute('aria-label') || '').trim();
          if (/record/i.test(label)) { e.preventDefault(); e.stopPropagation(); showModal(); setTimeout(goPro, 150); }
        };
        const opts = {capture:true, passive:false};
        document.addEventListener('click', handler, opts);
        document.addEventListener('pointerdown', handler, opts);
        document.addEventListener('touchstart', handler, opts);
      }

      function wireUI(){
        const open = document.getElementById('vb-tiktok-open-btn');
        const pro  = document.getElementById('vb-tiktok-use-pro');
        const dis  = document.getElementById('vb-tiktok-dismiss-btn');
        if (open) open.addEventListener('click', openExtern);
        if (pro)  pro.addEventListener('click', goPro);
        if (dis)  dis.addEventListener('click', ()=>{ hideModal(); try{ sessionStorage.setItem('vb-tiktok-dismissed','true'); }catch{} });
      }

      function init(){
        if (!(IS_TIKTOK || window.VB_IS_TIKTOK)) return;
        wireUI();
        interceptGUM();
        interceptRecordClicks();
        placeInlineHint();
        let dismissed = false; try { dismissed = sessionStorage.getItem('vb-tiktok-dismissed')==='true'; } catch {}
        if (!dismissed) showModal();
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          navigator.mediaDevices.getUserMedia({audio:true}).then(s=>s.getTracks().forEach(t=>t.stop())).catch(err=>console.log('[VB] TikTok expected mic failure:', err && (err.name+': '+err.message)));
        } else {
          console.log('[VB] getUserMedia unavailable (expected in TikTok webview).');
        }
      }

      // Fallback detection: if UA heuristics missed but it's a webview and NotAllowedError is thrown immediately, mark TikTok
      function fallbackProbe(){
        if (IS_TIKTOK || window.VB_IS_TIKTOK) return;
        if (!guessWebView) return;
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
        const start = Date.now();
        navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{ try{ s.getTracks().forEach(t=>t.stop()); }catch{} }).catch(err=>{
          const elapsed = Date.now()-start;
          if (err && err.name==='NotAllowedError' && elapsed < 350) {
            console.log('[VB] Fallback marking as TikTok based on immediate NotAllowedError in webview.');
            window.VB_IS_TIKTOK = true;
            try{ document.body.classList.add('vb-tiktok'); }catch{}
            wireUI(); interceptGUM(); interceptRecordClicks(); placeInlineHint(); showModal();
          }
        });
      }

      if (IS_TIKTOK || window.VB_IS_TIKTOK) {
        const tryNow = ()=>{ const el=document.getElementById('vb-tiktok-warning'); if (el){ el.classList.add('vb-show'); return true;} return false; };
        if (!tryNow()) { let n=0, id=setInterval(()=>{ n++; if (tryNow()||n>40) clearInterval(id); }, 50); }
      }
      if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
      if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', fallbackProbe); else setTimeout(fallbackProbe, 50);

      const mo = new MutationObserver(()=>{ if (IS_TIKTOK || window.VB_IS_TIKTOK) placeInlineHint(); });
      mo.observe(document.body, {childList:true, subtree:true});
    })();
    </script>
    """
    
    # Use st.html for better script execution, fallback to markdown
    try:
        html_func = getattr(st, "html", None)
        if callable(html_func):
            html_func(html)
        else:
            st.markdown(html, unsafe_allow_html=True)
    except Exception:
        st.markdown(html, unsafe_allow_html=True)
