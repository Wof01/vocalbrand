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

/* Main gradient background */
.main { 
    background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); 
    font-family: 'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; 
}

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
    color:white; 
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
}

.stButton>button:active {
    transform:translateY(0);
    box-shadow:0 4px 6px -1px rgba(0,0,0,.1);
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
        background: white !important;
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
    }
    
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
}

.stError {
    background: linear-gradient(90deg, #fef2f2 0%, #fee2e2 100%);
    border-left: 4px solid var(--error-red);
    border-radius: 8px;
    animation: slideIn .3s ease;
}

.stWarning {
    background: linear-gradient(90deg, #fffbeb 0%, #fef3c7 100%);
    border-left: 4px solid var(--warning-orange);
    border-radius: 8px;
    animation: slideIn .3s ease;
}

.stInfo {
    background: linear-gradient(90deg, #eff6ff 0%, #dbeafe 100%);
    border-left: 4px solid var(--primary-blue);
    border-radius: 8px;
    animation: slideIn .3s ease;
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
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 3px rgba(26, 54, 93, .1);
}

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
</style>
"""

def inject_css():
    st.markdown(SUPREME_CSS, unsafe_allow_html=True)

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
    from streamlit import markdown

    html = """
<!-- CSS-only mobile nav toggle: hidden checkbox controls sidebar and overlay -->
<input type="checkbox" id="vb-nav-toggle" class="vb-nav-toggle" aria-hidden="true" style="display:none" />
<label for="vb-nav-toggle" class="vb-fab-menu" id="vb-fab-menu" aria-label="Open navigation menu" title="Menu" tabindex="0"></label>
<label for="vb-nav-toggle" class="vb-nav-overlay" id="vb-nav-overlay" aria-hidden="true"></label>

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
// DESKTOP SIDEBAR TOGGLE FIX - ENSURE BUTTONS ALWAYS VISIBLE
// ============================================================
(function() {
    'use strict';
    
    console.log('VocalBrand: Initializing desktop sidebar toggle fix...');
    
    function isDesktopView() {
        return window.innerWidth >= 993;
    }
    
    function ensureSidebarButtonsVisible() {
        if (!isDesktopView()) {
            return; // Only run on desktop
        }
        
        // Find the sidebar
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) {
            return;
        }
        
        // Find the collapse button (inside sidebar when open)
        const collapseButton = sidebar.querySelector('button[kind="header"]');
        if (collapseButton) {
            // Ensure it's always visible
            collapseButton.style.visibility = 'visible';
            collapseButton.style.opacity = '1';
            collapseButton.style.display = 'flex';
            collapseButton.style.pointerEvents = 'auto';
        }
        
        // Find the expand button (appears when sidebar is collapsed)
        const expandControl = document.querySelector('[data-testid="collapsedControl"]');
        if (expandControl) {
            // Ensure container is visible
            expandControl.style.visibility = 'visible';
            expandControl.style.opacity = '1';
            expandControl.style.display = 'block';
            expandControl.style.position = 'fixed';
            expandControl.style.left = '0';
            expandControl.style.top = '50%';
            expandControl.style.transform = 'translateY(-50%)';
            expandControl.style.zIndex = '999999';
            
            // Find the button inside
            const expandButton = expandControl.querySelector('button');
            if (expandButton) {
                expandButton.style.visibility = 'visible';
                expandButton.style.opacity = '1';
                expandButton.style.display = 'flex';
                expandButton.style.pointerEvents = 'auto';
            }
        }
        
        // Alternative: look for the expand button directly
        const allButtons = document.querySelectorAll('button[kind="header"]');
        allButtons.forEach(btn => {
            if (!sidebar.contains(btn)) {
                // This is the expand button (outside sidebar)
                btn.style.visibility = 'visible';
                btn.style.opacity = '1';
                btn.style.display = 'flex';
                btn.style.pointerEvents = 'auto';
                btn.style.position = 'fixed';
                btn.style.left = '0';
                btn.style.top = '50%';
                btn.style.transform = 'translateY(-50%)';
                btn.style.zIndex = '999999';
            }
        });
    }
    
    // Run immediately
    ensureSidebarButtonsVisible();
    
    // Run on DOM changes (Streamlit redraws)
    const observer = new MutationObserver(function(mutations) {
        ensureSidebarButtonsVisible();
    });
    
    // Observe the entire document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'style', 'data-testid']
    });
    
    // Run on window resize
    window.addEventListener('resize', ensureSidebarButtonsVisible);
    
    // Run periodically as backup (every 500ms)
    setInterval(ensureSidebarButtonsVisible, 500);
    
    // Multiple retry attempts for Streamlit Cloud
    setTimeout(ensureSidebarButtonsVisible, 100);
    setTimeout(ensureSidebarButtonsVisible, 250);
    setTimeout(ensureSidebarButtonsVisible, 500);
    setTimeout(ensureSidebarButtonsVisible, 1000);
    setTimeout(ensureSidebarButtonsVisible, 2000);
    
    console.log('VocalBrand: Desktop sidebar toggle fix initialized ✓');
})();
</script>
    """
    markdown(html, unsafe_allow_html=True)
