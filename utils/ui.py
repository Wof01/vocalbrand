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
}

/* Accessible base theme — high contrast and brand colors */
/* App shell background kept light for readability */
.main { 
    background: #f8fafc; /* very light slate for neutral contrast */
    font-family: 'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; 
    color: #0f172a; /* slate-900 equivalent */
}

/* Make sure the outer container is also light (prevents dark rims) */
[data-testid="stAppViewContainer"], html, body { background: #f8fafc !important; color-scheme: light !important; }
[data-testid="stHeader"] { background: #ffffff00 !important; }

/* Global text color enforcement to fix faint/low-contrast text */
body, .stApp, .block-container,
[data-testid="stMarkdownContainer"],
h1, h2, h3, h4, h5, h6,
p, li, label, span, div,
code, pre, kbd, samp, strong, em {
    color: #0f172a !important; /* dark text everywhere */
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

/* Primary buttons with hover effects */
.stButton>button { 
    background:linear-gradient(135deg,var(--primary-blue) 0%, #2d3748 100%); 
    color:#ffffff !important; /* Ensure white text for maximum contrast on blue */
    border:none; 
    padding:.75rem 2rem; 
    border-radius:12px; 
    font-weight:600; 
    font-size:1rem; 
    transition:all .3s ease; 
    box-shadow:0 4px 6px -1px rgba(0,0,0,.1);
    min-height:44px; /* Touch-friendly */
}

.stButton>button:hover { 
    transform:translateY(-2px); 
    box-shadow:0 10px 15px -3px rgba(0,0,0,.2); 
    background:linear-gradient(135deg,#2d3748 0%, var(--primary-blue) 100%);
    color:#ffffff !important; /* Preserve white text on hover */
}

.stButton>button:active {
    transform:translateY(0);
    box-shadow:0 4px 6px -1px rgba(0,0,0,.1);
}
/* Disabled primary buttons should still use white text for legibility */
.stButton>button:disabled, .stButton>button[disabled] {
    color:#ffffff !important; opacity:.6;
}

/* Ensure icons within buttons are visible on dark backgrounds */
.stButton>button svg { color:#ffffff !important; fill:#ffffff !important; }

/* Apply consistent white text to other Streamlit button variants */
.stDownloadButton>button,
.stFormSubmitButton>button {
    color:#ffffff !important;
}
/* Link buttons rendered as anchors */
.stLinkButton a,
.stLinkButton>a,
.stLinkButton button,
.stLinkButton [data-testid="baseButton-primary"] {
    color:#ffffff !important;
}
[data-testid="stLinkButton"] a { color:#ffffff !important; }

/* Streamlit's new unified base button test id — enforce white text for primary buttons */
[data-testid="baseButton-primary"] { color:#ffffff !important; }
[data-testid="baseButton-primary"] svg { color:#ffffff !important; fill:#ffffff !important; }
[data-testid="baseButton-primary"][aria-disabled="true"] { color:#ffffff !important; opacity:.6; }
[data-testid="baseButton-primary"] * { color:#ffffff !important; fill:#ffffff !important; }

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

/* Tabs — ensure clear selected state and readable labels */
/* BaseWeb and Streamlit tabs variants */
div[data-testid="stTabs"] [role="tab"],
.stTabs [role="tab"],
div[data-baseweb="tab-list"] button { color: #0f172a !important; background: #e2e8f0 !important; border-radius: 10px !important; }
div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
.stTabs [role="tab"][aria-selected="true"],
div[data-baseweb="tab-list"] button[aria-selected="true"] {
    background: var(--primary-blue) !important;
    color: #ffffff !important;
}
/* Ensure inner text inside selected tabs is white */
.stTabs [role="tab"][aria-selected="true"] *,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] *,
div[data-baseweb="tab-list"] button[aria-selected="true"] * { color:#ffffff !important; fill:#ffffff !important; }
/* Ensure unselected tabs use dark readable text */
.stTabs [role="tab"]:not([aria-selected="true"]) *,
div[data-testid="stTabs"] [role="tab"]:not([aria-selected="true"]) *,
div[data-baseweb="tab-list"] button:not([aria-selected="true"]) * { color:#0f172a !important; }
div[data-testid="stTabs"] [role="tab"]:focus,
.stTabs [role="tab"]:focus,
div[data-baseweb="tab-list"] button:focus { outline: 3px solid var(--accent-gold) !important; outline-offset: 2px; }

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
section[data-testid="stSidebar"] .stButton>button { 
    width: 100%; 
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
.stSuccess {
    background: linear-gradient(90deg, #ecfdf5 0%, #d1fae5 100%);
    border-left: 4px solid var(--success-green);
    border-radius: 8px;
    animation: slideIn .3s ease;
    color: #064e3b !important;
}

.stError {
    background: linear-gradient(90deg, #fef2f2 0%, #fee2e2 100%);
    border-left: 4px solid var(--error-red);
    border-radius: 8px;
    animation: slideIn .3s ease;
    color: #7f1d1d !important;
}

.stWarning {
    background: linear-gradient(90deg, #fffbeb 0%, #fef3c7 100%);
    border-left: 4px solid var(--warning-orange);
    border-radius: 8px;
    animation: slideIn .3s ease;
    color: #78350f !important;
}

.stInfo {
    background: linear-gradient(90deg, #eff6ff 0%, #dbeafe 100%);
    border-left: 4px solid var(--primary-blue);
    border-radius: 8px;
    animation: slideIn .3s ease;
    color: #0f172a !important;
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
        right: 1rem; 
        bottom: 1rem; 
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
        left: 0;
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
</style>
"""

def inject_css():
    st.markdown(SUPREME_CSS, unsafe_allow_html=True)
    # Subtle UI polish for pricing/link buttons in the sidebar
    st.markdown(
        """
        <style>
        /* Primary actions (global): ensure white text/icons on brand-blue buttons */
        [data-testid="baseButton-primary"],
        [data-testid="baseButton-primary"] *,
        .stButton>button[kind="primary"],
        .stButton>button[kind="primary"] * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        /* Any Streamlit button using our dark-blue background should enforce white text for all descendants */
        .stButton>button,
        .stButton>button * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        /* Disabled primary buttons keep readable contrast */
        [data-testid="baseButton-primary"][disabled],
        .stButton>button[kind="primary"]:disabled {
            color: rgba(255,255,255,.85) !important;
        }

        /* Global polish for link buttons */
        [data-testid="stLinkButton"] button,
        a[data-testid="stLinkButton"] {
            min-height: 40px !important;
            border-radius: 10px !important;
            padding: 0 14px !important;
            box-shadow: 0 3px 8px rgba(0,0,0,.08) !important;
            font-weight: 600 !important;
        }

        section[data-testid="stSidebar"] .stButton>button,
        section[data-testid="stSidebar"] [data-testid="stLinkButton"] button,
        section[data-testid="stSidebar"] [data-testid="stLinkButton"] a,
        section[data-testid="stSidebar"] a[data-testid="stLinkButton"] {
            width: 100% !important;
            min-height: 42px !important;
            border-radius: 10px !important;
            padding: 0 14px !important;
            box-shadow: 0 3px 8px rgba(0,0,0,.08) !important;
        }
        
        /* Color hierarchy for pricing */
        section[data-testid="stSidebar"] button[key*="upgrade_btn"],
        section[data-testid="stSidebar"] button[key*="setup_"],
        section[data-testid="stSidebar"] button[key*="pack_"],
        section[data-testid="stSidebar"] button[key*="setup_"][key*="price_"],
        section[data-testid="stSidebar"] button[key*="pack_"][key*="price_"] {
            background: linear-gradient(135deg, var(--primary-blue) 0%, #0b2344 100%) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
        }
        /* And ensure their inner spans/icons also stay white */
        section[data-testid="stSidebar"] button[key*="upgrade_btn"] *,
        section[data-testid="stSidebar"] button[key*="setup_"] *,
        section[data-testid="stSidebar"] button[key*="pack_"] *,
        section[data-testid="stSidebar"] button[key*="setup_"][key*="price_"] *,
        section[data-testid="stSidebar"] button[key*="pack_"][key*="price_"] * {
            color:#ffffff !important; fill:#ffffff !important;
        }
        /* Apply same treatment to payment link buttons (anchors) */
        section[data-testid="stSidebar"] [data-testid="stLinkButton"] a,
        section[data-testid="stSidebar"] a[data-testid="stLinkButton"] {
            background: linear-gradient(135deg, var(--primary-blue) 0%, #0b2344 100%) !important;
            color:#ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            display: block !important;
            text-align: center !important;
        }
        /* Guarantee children inside link buttons are white too */
        [data-testid="stLinkButton"] *,
        section[data-testid="stSidebar"] [data-testid="stLinkButton"] * {
            color:#ffffff !important; fill:#ffffff !important;
        }
        
        /* Compact the right column a bit and create breathing room between rows */
        section[data-testid="stSidebar"] [data-testid="column"] {
            margin-bottom: .35rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
                    z-index: 999999 !important;
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
