"""UI helpers for VocalBrand Streamlit app."""
from __future__ import annotations
import streamlit as st
from typing import Iterable, List, Optional

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
/* Sidebar markdown and all descendants must never reintroduce white backplates */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
    background: transparent !important;
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
.stAlert, [data-baseweb="notification"], div[role="alert"] {
    background: #eff6ff !important;
    color: var(--dark-text) !important;
    border: 1px solid #93c5fd !important;
}
/* Ensure alert content never paints white slabs inside */
.stAlert *, [data-baseweb="notification"] *, div[role="alert"] * {
    background: transparent !important;
}

/* Sidebar alerts should be subtle and transparent */
section[data-testid="stSidebar"] .stAlert,
section[data-testid="stSidebar"] div[role="alert"],
section[data-testid="stSidebar"] [data-baseweb="notification"] {
    background: transparent !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: none !important;
}

/* ===============================
   FILE UPLOADER - LIGHT THEME
   Ensure visible drop zone and labels
   =============================== */
/* Make the uploader shell fully transparent to avoid white artifacts,
   keep a strong dashed border for affordance. */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] .uploadDropTarget,
.stFileUploader,
.stFileUploader section,
.stFileUploader .uploadDropTarget {
    background: transparent !important; /* prevent inner white slabs */
    border: 3px dashed var(--primary-blue) !important; /* brand-color border */
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

/* If the uploader is placed inside brand/gradient panels, ensure no child reintroduces white. */
.vb-banner--upgrade [data-testid="stFileUploader"],
.vb-banner--upgrade .stFileUploader,
.vb-banner--upgrade [data-testid="stFileUploader"] *,
.vb-banner--upgrade .stFileUploader * {
    background: transparent !important;
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
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    color: var(--dark-text) !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0.75rem !important;
    border-bottom: 3px solid var(--light-slate) !important;
    display: block !important;
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
.vb-banner--upgrade {
    background:linear-gradient(135deg, var(--primary-blue) 0%, #0b2344 100%) !important;
    color:#fff !important;
    border-color:#0b2344 !important;
    display:block !important;
    position:relative !important;
    isolation:isolate !important; /* ensure gradient is not washed by ancestors */
}
.vb-banner--upgrade { color:#ffffff !important; }
/* Important: only descendants get background reset to prevent wiping the banner gradient */
.vb-banner--upgrade * { color:#ffffff !important; fill:#ffffff !important; background:transparent !important; }
.vb-banner--upgrade .vb-banner__title { font-weight:800; font-size:1.2rem; }
.vb-banner--upgrade .vb-banner__sub { opacity:.92; }

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

/* ===============================
   ENHANCED SIDEBAR NAVIGATION
   =============================== */

/* Ensure radio buttons stack vertically with proper spacing */
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] [role="radio"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    padding: 1.25rem 1rem !important; /* Increased padding for clarity */
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    white-space: normal !important;
    word-wrap: break-word !important;
}

/* Highlight selected radio option with enhanced visibility */
section[data-testid="stSidebar"] .stRadio label:has(input:checked),
section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
    background: linear-gradient(135deg, rgba(26, 54, 93, 0.25) 0%, rgba(26, 54, 93, 0.15) 100%) !important;
    border-left: 6px solid var(--primary-blue) !important; /* Enhanced border for visibility */
    font-weight: 700 !important;
}

/* Ensure radio input is visible and styled */
section[data-testid="stSidebar"] .stRadio input[type="radio"],
section[data-testid="stSidebar"] [role="radio"] input {
    flex-shrink: 0 !important;
    margin-right: 1.25rem !important; /* Increased margin for spacing */
    width: 28px !important; /* Slightly larger for better visibility */
    height: 28px !important;
    visibility: visible !important;
    opacity: 1 !important;
    accent-color: var(--primary-blue) !important;
    position: relative !important;
    z-index: 1 !important;
}

/* Add Navigation section header styling */
section[data-testid="stSidebar"] .stRadio > label:first-child,
section[data-testid="stSidebar"] [role="radiogroup"] > div:first-child {
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    color: var(--dark-text) !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0.75rem !important;
    border-bottom: 3px solid var(--light-slate) !important;
    display: block !important;
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
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    color: var(--dark-text) !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0.75rem !important;
    border-bottom: 3px solid var(--light-slate) !important;
    display: block !important;
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

/* ===============================
   ENHANCED SIDEBAR NAVIGATION
   =============================== */

/* Ensure radio buttons stack vertically with proper spacing */
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] [role="radio"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    padding: 1.25rem 1rem !important; /* Increased padding for clarity */
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    white-space: normal !important;
    word-wrap: break-word !important;
}

/* Highlight selected radio option with enhanced visibility */
section[data-testid="stSidebar"] .stRadio label:has(input:checked),
section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
    background: linear-gradient(135deg, rgba(26, 54, 93, 0.25) 0%, rgba(26, 54, 93, 0.15) 100%) !important;
    border-left: 6px solid var(--primary-blue) !important; /* Enhanced border for visibility */
    font-weight: 700 !important;
}

/* Ensure radio input is visible and styled */
section[data-testid="stSidebar"] .stRadio input[type="radio"],
section[data-testid="stSidebar"] [role="radio"] input {
    flex-shrink: 0 !important;
    margin-right: 1.25rem !important; /* Increased margin for spacing */
    width: 28px !important; /* Slightly larger for better visibility */
    height: 28px !important;
    visibility: visible !important;
    opacity: 1 !important;
    accent-color: var(--primary-blue) !important;
    position: relative !important;
    z-index: 1 !important;
}

/* Add Navigation section header styling */
section[data-testid="stSidebar"] .stRadio > label:first-child,
section[data-testid="stSidebar"] [role="radiogroup"] > div:first-child {
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    color: var(--dark-text) !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0.75rem !important;
    border-bottom: 3px solid var(--light-slate) !important;
    display: block !important;
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
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    color: var(--dark-text) !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0.75rem !important;
    border-bottom: 3px solid var(--light-slate) !important;
    display: block !important;
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
}
/* End SUPREME_CSS core */
</style>
"""


def inject_css() -> None:
    """Inject the global SUPREME_CSS into the app.

    Kept additive-only and safe for repeated calls.
    """
    st.markdown(SUPREME_CSS, unsafe_allow_html=True)
    # Add focused hotfix styles to reinforce visibility and remove residual artifacts
    EXTRA_CSS = """
        <style>
            /* Sidebar radio labels: make text unambiguously visible */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label,
            section[data-testid="stSidebar"] [role="radiogroup"] > label,
            section[data-testid="stSidebar"] [role="radiogroup"] [role="radio"]{
                color: var(--dark-text) !important;
                font-size: 0.96rem !important;
                line-height: 1.35 !important;
                white-space: normal !important;
            }
                    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label *,
                    section[data-testid="stSidebar"] [role="radiogroup"] > label *,
                    section[data-testid="stSidebar"] [role="radiogroup"] [role="radio"] *{
                        color: var(--dark-text) !important;
                        -webkit-text-fill-color: var(--dark-text) !important;
                    }

            /* Primary/secondary button text must remain visible */
            .stButton > button, .stDownloadButton > button{
                font-weight: 700 !important; min-height: 44px !important; border-radius: 12px !important;
            }
            .stButton > button span, .stButton > button *{ color: inherit !important; }

            /* Remove white inner artifacts within gradient CTAs we render via HTML */
            div[style*="linear-gradient(135deg"] *,
            div[style*="linear-gradient(90deg"] *{
                background: transparent !important;
            }

            /* Ensure markdown/element wrappers never paint white backplates */
                    .element-container, [data-testid="stMarkdownContainer"],
                    [data-testid="stMarkdownContainer"] *{
                background: transparent !important;
                box-shadow: none !important; border: none !important;
            }
        </style>
        """
    st.markdown(EXTRA_CSS, unsafe_allow_html=True)


def inject_mobile_nav_helpers() -> None:
    """Install lightweight sidebar/mobile helpers.

    Currently a thin wrapper that applies alignment, visibility and audio-player
    fixes contained in `inject_supreme_sidebar_and_audio_fix()`.
    """
    inject_supreme_sidebar_and_audio_fix()


def render_steps(current: int, total: int, labels: Optional[List[str]] = None) -> None:
    """Render a clean, accessible horizontal stepper.

    Args:
        current: 1-based index of the active step.
        total: total number of steps.
        labels: optional list of step labels; if provided and length mismatches
            total, it will be padded/truncated safely.

    Notes:
        - Pure HTML/CSS; no JS. Works in light theme and preserves your brand colors.
        - Safe to call multiple times; style block is id-scoped to avoid duplicates.
    """
    if total < 1:
        total = 1
    if current < 1:
        current = 1
    if current > total:
        current = total

    default_labels = [
        "Record sample",
        "Clone voice",
        "Write script",
        "Generate speech",
    ]
    if labels is None:
        labels = default_labels[:total] + [""] * max(0, total - len(default_labels))
    else:
        # Normalize length
        labels = (labels + [""] * total)[:total]

    # Build the steps markup
    items_html = []
    for i in range(1, total + 1):
        state = "done" if i < current else ("active" if i == current else "todo")
        label = labels[i - 1]
        items_html.append(
            f'<li class="vb-step {state}"><span class="dot">{i}</span><span class="lbl">{label}</span></li>'
        )
    steps_html = "\n".join(items_html)

    html = f"""
    <style id="vb-steps-style">
      .vb-steps {{
        display: grid; grid-template-columns: repeat({total}, 1fr);
        gap: 10px; margin: 0.75rem 0 1.25rem 0; padding: 0; list-style: none;
      }}
      .vb-step {{
        position: relative; display: flex; align-items: center; gap: 10px;
        background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 10px 12px; color: var(--dark-text);
      }}
      .vb-step .dot {{
        width: 24px; height: 24px; border-radius: 999px; display: inline-flex;
        align-items: center; justify-content: center; font-weight: 800; font-size: 12px;
        background: #e2e8f0; color: #0f172a; border: 1px solid #cbd5e1;
        flex: none;
      }}
      .vb-step .lbl {{
        font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      }}
      .vb-step.active {{
        border-color: var(--primary-blue); background: linear-gradient(180deg, rgba(30,58,138,0.06), rgba(30,58,138,0.03));
        box-shadow: 0 2px 8px rgba(2,6,23,0.06);
      }}
      .vb-step.active .dot {{ background: var(--primary-blue); color: #fff; border-color: var(--primary-blue); }}
      .vb-step.done .dot {{ background: #10b981; color: #fff; border-color: #059669; }}
      @media (max-width: 720px) {{ .vb-step .lbl {{ display: none; }} }}
    </style>
    <ul class="vb-steps">{steps_html}</ul>
    """

    # Prefer st.html when available to avoid Markdown treating leading spaces as code
    html_out = html.strip()
    try:
        html_func = getattr(st, "html", None)
        if callable(html_func):
            html_func(html_out)
        else:
            st.markdown(html_out, unsafe_allow_html=True)
    except Exception:
        st.markdown(html_out, unsafe_allow_html=True)


def vb_stat_card(variant: str, value: str, label: str, sublabel: str = "") -> None:
    """Render a compact stat card used on the onboarding page.

    Variants: "success" (green), "info" (blue), "brand" (gold/brand).
    Safe defaults are applied for unknown variants.
    """
    variant = (variant or "").lower()
    if variant == "success":
        bg = "linear-gradient(135deg, rgba(16,185,129,.12), rgba(16,185,129,.05))"
        border = "#34d399"
        pill = "#10b981"
        pill_text = "#ffffff"
    elif variant == "brand":
        bg = "linear-gradient(135deg, rgba(212,175,55,.12), rgba(26,54,93,.05))"
        border = "#d4af37"
        pill = "#d4af37"
        pill_text = "#0f172a"
    else:  # info / default
        bg = "linear-gradient(135deg, rgba(37,99,235,.10), rgba(30,64,175,.05))"
        border = "#60a5fa"
        pill = "#2563eb"
        pill_text = "#ffffff"

    html = f"""
    <div class="vb-stat" style="background:{bg};border:1px solid {border};border-radius:14px;padding:16px 14px;display:flex;flex-direction:column;gap:6px;box-shadow:0 4px 14px rgba(2,6,23,.06);">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="display:inline-flex;align-items:center;justify-content:center;padding:2px 10px;border-radius:999px;background:{pill};color:{pill_text};font-weight:800;font-size:.8rem;letter-spacing:.03em;">{label}</span>
        <span style="color:#64748b;font-weight:700;">{sublabel}</span>
      </div>
      <div style="font-size:1.8rem;font-weight:800;color:var(--dark-text);line-height:1;">{value}</div>
    </div>
    """
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
            /* Keep existing look; enforce a fixed dot column + text column */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"]{
                margin: 0.25rem 0 !important;
                position: relative !important;
            }
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label{
                display: flex !important;
                align-items: center !important;
                gap: 0.625rem !important;
                padding: 0.45rem 0.9rem !important; /* a touch taller for legibility */
                margin: 0.125rem 0 !important;
                white-space: nowrap !important; /* keep label text inside the button */
                border-left: 2px solid #e2e8f0 !important; /* faint gutter visible even when not selected */
                overflow: visible !important;
                text-overflow: initial !important;
                color: var(--dark-text) !important;
                -webkit-text-fill-color: var(--dark-text) !important;
                min-height: 38px !important;
                line-height: 1.2 !important;
                width: 100% !important;
                background: transparent !important;
            }
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label input[type="radio"]{
                width: 18px !important;
                height: 18px !important;
                margin: 0 !important; /* grid controls spacing */
                justify-self: start !important;
                align-self: center !important;
            }
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label span,
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label div{
                display: inline-flex !important;
                align-items: center !important;
                min-width: 0 !important;
                color: var(--dark-text) !important;
                -webkit-text-fill-color: var(--dark-text) !important;
            }

            /* Step badges appear before labels when data-vb-step is set */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label[data-vb-step]::before{
                content: attr(data-vb-step);
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 20px; height: 20px;
                font-size: 11px; font-weight: 800;
                color: #0f172a;
                background: #e2e8f0;
                border: 1px solid #cbd5e1;
                border-radius: 999px;
                margin-right: .35rem;
                grid-column: 2; /* place in text lane just before text */
            }
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label[aria-checked="true"][data-vb-step]::before,
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label:has(input:checked)[data-vb-step]::before{
                background: var(--primary-blue);
                border-color: var(--primary-blue);
                color: #fff;
            }

            /* Selected state: premium highlight without offsetting alignment */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label[aria-checked="true"]{
                background: linear-gradient(180deg, rgba(30,58,138,0.06), rgba(30,58,138,0.03)) !important;
                box-shadow: 0 2px 8px rgba(2,6,23,0.06) !important;
                border-left-width: 4px !important;
                border-left-color: var(--primary-blue) !important; /* activate gutter */
                color: var(--primary-blue) !important;
                -webkit-text-fill-color: var(--primary-blue) !important;
                font-weight: 700 !important;
            }

            /* Hover focus affordance */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label:hover{
                background: linear-gradient(180deg, rgba(226,232,240,0.45), rgba(226,232,240,0.25)) !important;
                border-left-color: #94a3b8 !important;
            }

            /* Ensure the whole nav block fits; if not, sidebar scrolls (see container rule above) */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"]{
                margin-bottom: 0.5rem !important;
            }

            /* Optional: secondary headers inside the same group (added via JS) */
            section[data-testid="stSidebar"] .vb-nav-header,
            section[data-testid="stSidebar"] .vb-nav-subheader{
                display: block !important;
                grid-template-columns: 1fr !important;
                border-left-color: transparent !important;
                color: #64748b !important;
                font-weight: 800 !important;
                letter-spacing: 0.1em !important;
                text-transform: uppercase !important;
                background: transparent !important;
                cursor: default !important;
                pointer-events: none !important;
            }
            section[data-testid="stSidebar"] .vb-nav-header{ position: sticky !important; top: 0 !important; z-index: 3 !important; background:#f8fafc !important; }
            section[data-testid="stSidebar"] .vb-nav-subheader{ margin-top: .35rem !important; margin-bottom: .15rem !important; }

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

            /* Scroll overflow hints */
            section[data-testid="stSidebar"] .vb-scroll-hint{ position: sticky; left: 0; right: 0; height: 18px; pointer-events: none; z-index: 5; }
            section[data-testid="stSidebar"] .vb-scroll-hint.top{ top: 0; background: linear-gradient(180deg, rgba(248,250,252,1), rgba(248,250,252,0)); display: none; }
            section[data-testid="stSidebar"] .vb-scroll-hint.bottom{ bottom: 0; background: linear-gradient(0deg, rgba(248,250,252,1), rgba(248,250,252,0)); display: none; }
            section[data-testid="stSidebar"] .vb-scroll-hint.vb-show{ display: block; }

            /* ---------- Sidebar Upgrade CTA (visible above "Pro Features") ---------- */
            section[data-testid="stSidebar"] .vb-sidebar-cta{
                display:block !important;
                background: linear-gradient(135deg, #1e3a8a 0%, #0b2344 100%) !important;
                color:#fff !important; border-radius:14px !important; padding:12px 14px !important;
                box-shadow: 0 6px 18px rgba(2,6,23,.18) !important; border:1px solid rgba(255,255,255,.15) !important;
                margin: .5rem 0 0.75rem 0 !important; position:relative !important; overflow:hidden !important;
            }
            section[data-testid="stSidebar"] .vb-sidebar-cta *,
            section[data-testid="stSidebar"] .vb-sidebar-cta .sub{ color:#fff !important; background:transparent !important; }
            section[data-testid="stSidebar"] .vb-sidebar-cta .ttl{ font-weight:800; font-size:1rem; margin:0 0 .25rem 0; }
            section[data-testid="stSidebar"] .vb-sidebar-cta .sub{ font-weight:600; opacity:.92; line-height:1.35; }

            /* ---------- Mobile FAB to open sidebar ---------- */
            @media (max-width: 992px){
                #vb-fab-menu{ position: fixed !important; right: 18px !important; left:auto !important; bottom: 18px !important; width:60px; height:60px; border-radius:50%;
                    background: linear-gradient(180deg, #15335f 0%, #0b2344 100%) !important;
                    color:#fff; border:none; box-shadow:0 14px 30px rgba(2,6,23,.35) !important;
                    display:flex; align-items:center; justify-content:center; z-index: 99999 !important; cursor:pointer;
                    transition: transform .15s ease, box-shadow .2s ease, opacity .25s ease; opacity: .98; }
                #vb-fab-menu:hover{ transform: translateY(-2px) scale(1.03); box-shadow:0 18px 36px rgba(2,6,23,.4); }
                #vb-fab-menu:active{ transform: scale(.98); }
                #vb-fab-menu svg{ width: 28px; height: 28px; display:block; }
                #vb-fab-menu[hidden]{ display:none !important; }

                /* Hide native toggles; we'll render a unified top-bar toggle */
                [data-testid="collapsedControl"],
                [data-testid="stSidebarNavOpen"],
                [data-testid="stSidebarNavClose"]{ opacity: 0 !important; pointer-events: none !important; }

                /* Our unified mobile top bar toggle */
                #vb-topbar-toggle{ position: fixed !important; top: 12px !important; left: 12px !important; width: 36px; height: 36px;
                    display: inline-flex; align-items:center; justify-content:center; border-radius: 999px; z-index: 100000 !important;
                    background: #0b2344; color: #fff; box-shadow: 0 8px 18px rgba(2,6,23,.25); font-size: 18px; font-weight: 900; }
                #vb-topbar-toggle span{ line-height: 1; display:block; transform: translateY(-1px); }
                #vb-topbar-toggle:active{ transform: scale(.98); }
                /* Avoid header content overlap by giving left padding */
                [data-testid="stHeader"]{ padding-left: 56px !important; }
            }
            /* Ensure topbar toggle is styled even on mobile UA devices with large CSS pixels */
            #vb-topbar-toggle{ position: fixed; top: 12px; left: 12px; width: 36px; height: 36px;
                display: inline-flex; align-items:center; justify-content:center; border-radius: 999px; z-index: 100000;
                background: #0b2344; color: #fff; box-shadow: 0 8px 18px rgba(2,6,23,.25); font-size: 18px; font-weight: 900; }
            #vb-topbar-toggle span{ line-height: 1; display:block; transform: translateY(-1px); }
            #vb-topbar-toggle:active{ transform: scale(.98); }
            .vb-has-topbar-toggle [data-testid="stHeader"]{ padding-left: 56px !important; }
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

            // 🎯 PART 2: Navigation helpers — ensure selected item is visible, mark headers, add steps, and show scroll hints

            function getSidebar(){
                return document.querySelector('[data-testid="stSidebar"]') || document.querySelector('section[data-testid="stSidebar"]');
            }

            function labelText(el){ return (el && (el.innerText || '').trim()) || ''; }

            function markHeaders(sidebar){
                if (!sidebar) return;
                // Insert a "Navigation" header above the first radiogroup if missing.
                const rg = sidebar.querySelector('.stRadio > div[role="radiogroup"]');
                if (!rg) return;
                const maybeHeader = rg.previousElementSibling;
                const already = maybeHeader && maybeHeader.classList && maybeHeader.classList.contains('vb-nav-header');
                if (!already){
                    const hdr = document.createElement('div');
                    hdr.className = 'vb-nav-header';
                    hdr.textContent = 'Navigation';
                    try { rg.parentElement.insertBefore(hdr, rg); } catch {}
                }
            }

            function addStepBadges(sidebar){
                if (!sidebar) return;
                const map = [
                    {re: /(record|upload).*sample|record/i, step: '1'},
                    {re: /(clone).*voice/i, step: '2'},
                    {re: /(write|create).*script|text/i, step: '3'},
                    {re: /(generate|create).*audio|speech/i, step: '4'}
                ];
                const labels = sidebar.querySelectorAll('.stRadio label, [role="radiogroup"] > label');
                labels.forEach(l => {
                    const txt = (l.innerText||'').toLowerCase();
                    for (const r of map){
                        if (r.re.test(txt)) { l.setAttribute('data-vb-step', r.step); break; }
                    }
                });
            }

            function scrollSelectedIntoView(sidebar){
                if (!sidebar) return;
                const sel = sidebar.querySelector('[role="radio"][aria-checked="true"], label:has(input:checked)');
                if (sel && sel.scrollIntoView) {
                    try { sel.scrollIntoView({behavior:'smooth', block:'nearest', inline:'nearest'}); }
                    catch { sel.scrollIntoView(); }
                }
            }

            function ensureScrollHints(sidebar){
                if (!sidebar) return;
                let top = sidebar.querySelector('.vb-scroll-hint.top');
                let bottom = sidebar.querySelector('.vb-scroll-hint.bottom');
                if (!top){
                    top = document.createElement('div'); top.className = 'vb-scroll-hint top'; sidebar.prepend(top);
                }
                if (!bottom){
                    bottom = document.createElement('div'); bottom.className = 'vb-scroll-hint bottom'; sidebar.appendChild(bottom);
                }
                function update(){
                    const max = sidebar.scrollHeight - sidebar.clientHeight;
                    const y = sidebar.scrollTop;
                    if (y > 2) top.classList.add('vb-show'); else top.classList.remove('vb-show');
                    if (y < max - 2) bottom.classList.add('vb-show'); else bottom.classList.remove('vb-show');
                }
                update();
                sidebar.addEventListener('scroll', update, {passive:true});
                window.addEventListener('resize', update);
                const mo = new MutationObserver(update); mo.observe(sidebar, {childList:true, subtree:true});
            }

            function enhanceNav(){
                const sb = getSidebar();
                if (!sb) return;
                markHeaders(sb);
                addStepBadges(sb);
                scrollSelectedIntoView(sb);
                ensureScrollHints(sb);
            }
            enhanceNav();

            const moNav = new MutationObserver(() => enhanceNav());
            moNav.observe(document.body, {subtree:true, childList:true, attributes:true, attributeFilter:['aria-checked','class','style']});

            console.log('[VB] 🎯 Supreme sidebar and audio fixes loaded');

            // 🔹 Sidebar Upgrade CTA injector (appears above "Pro Features:" in sidebar)
            (function ensureSidebarCTA(){
                const mount = ()=>{
                    try{
                        const sb = document.querySelector('section[data-testid="stSidebar"]');
                        if (!sb) return;
                        const content = sb.querySelector('[data-testid="stSidebarContent"]') || sb;
                        if (content.querySelector('.vb-sidebar-cta')) return;
                        const card = document.createElement('div');
                        card.className = 'vb-sidebar-cta';
                        card.innerHTML = '<div class="ttl">Upgrade to VocalBrand Pro</div><div class="sub">Unlimited generations • Priority processing • Commercial use</div>';
                        content.insertBefore(card, content.firstChild);
                    }catch(e){ console.log('[VB] Sidebar CTA inject skipped:', e); }
                };
                mount();
                // Keep robust against Streamlit reruns
                const sbRoot = document.querySelector('section[data-testid="stSidebar"]');
                if (sbRoot && 'MutationObserver' in window){
                    const mo = new MutationObserver(()=> mount());
                    mo.observe(sbRoot, {childList:true, subtree:true});
                }
            })();

            // 🔹 Mobile FAB button that opens the sidebar (<= 992px)
            (function ensureFab(){
                try{
                    if (document.getElementById('vb-fab-menu')) return;
                    if (!window.matchMedia || !window.matchMedia('(max-width: 992px)').matches) return;
                    const btn = document.createElement('button');
                    btn.id = 'vb-fab-menu'; btn.setAttribute('aria-label','Open menu'); btn.setAttribute('title','Menu');
                    btn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><g stroke="white" stroke-width="2.2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></g></svg>';
                    document.body.appendChild(btn);
                    const toggleSidebar = () => {
                        // Try the dedicated open control first
                        const h = document.querySelector('[data-testid="stSidebarNavOpen"] button');
                        if (h) { try{ h.click(); return true; }catch{} }
                        // Then the collapsed control (toggles open/close)
                        const cc = document.querySelector('[data-testid="collapsedControl"] button, div[data-testid="collapsedControl"] > button');
                        if (cc) { try{ cc.click(); return true; }catch{} }
                        return false;
                    };
                    const handler = (e)=>{ e.preventDefault(); e.stopPropagation(); toggleSidebar(); };
                    ['click','touchstart','pointerdown','mousedown','keydown'].forEach(ev=> btn.addEventListener(ev, handler, {passive:false}));
                    // Hide FAB while sidebar overlay is visible to avoid overlap
                    const sb = document.querySelector('section[data-testid="stSidebar"]');
                    if (sb && 'MutationObserver' in window){
                        const mo = new MutationObserver(()=>{
                            const overlay = document.querySelector('[data-testid="stSidebarOverlay"]');
                            if (overlay && getComputedStyle(overlay).display !== 'none') btn.setAttribute('hidden','');
                            else btn.removeAttribute('hidden');
                            // Enforce position bottom-right in case any baseline CSS sets left
                            btn.style.right = '18px'; btn.style.left = 'auto'; btn.style.bottom = '18px'; btn.style.position = 'fixed';
                        });
                        mo.observe(document.body, {childList:true, subtree:true});
                    }
                    // Safety: enforce position once on mount
                    btn.style.right = '18px'; btn.style.left = 'auto'; btn.style.bottom = '18px'; btn.style.position = 'fixed';
                    console.log('[VB] ✓ FAB initialized');
                }catch(e){ console.log('[VB] FAB inject skipped:', e); }
            })();

            // 🔹 Unified top-bar toggle (» to open / « to close) on mobile
            (function ensureTopbarToggle(){
                try{
                    const isMobileUA = /Mobi|Android|iPhone|iPad|iPod|Windows Phone|Opera Mini|IEMobile/i.test(navigator.userAgent||'');
                    const isNarrow = (window.matchMedia && window.matchMedia('(max-width: 992px)').matches);
                    if (!(isNarrow || isMobileUA)) return;
                    if (document.getElementById('vb-topbar-toggle')) return;
                    const btn = document.createElement('button');
                    btn.id = 'vb-topbar-toggle'; btn.type = 'button'; btn.setAttribute('aria-label','Toggle menu');
                    const setIcon = () => {
                        const overlay = document.querySelector('[data-testid="stSidebarOverlay"]');
                        const open = overlay && getComputedStyle(overlay).display !== 'none';
                        btn.innerHTML = open ? '<span>&laquo;</span>' : '<span>&raquo;</span>';
                    };
                    const doToggle = () => {
                        const overlay = document.querySelector('[data-testid="stSidebarOverlay"]');
                        const openEl = document.querySelector('[data-testid="stSidebarNavOpen"] button, [data-testid="collapsedControl"] button');
                        const closeEl = document.querySelector('[data-testid="stSidebarNavClose"] button, [data-testid="collapsedControl"] button');
                        const open = overlay && getComputedStyle(overlay).display !== 'none';
                        try { (open ? closeEl : openEl)?.click(); } catch {}
                        setTimeout(setIcon, 60);
                    };
                    btn.addEventListener('click', (e)=>{ e.preventDefault(); e.stopPropagation(); doToggle(); });
                    document.body.appendChild(btn);
                    try{ document.body.classList.add('vb-has-topbar-toggle'); }catch{}
                    setIcon();
                    if ('MutationObserver' in window){
                        const mo = new MutationObserver(setIcon);
                        mo.observe(document.body, {childList:true, subtree:true, attributes:true});
                    }
                    console.log('[VB] ✓ Topbar toggle initialized');
                }catch(e){ console.log('[VB] Topbar toggle skipped:', e); }
            })();
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
