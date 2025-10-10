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
    
    /* Ensure sidebar overlay sits above content */
    section[data-testid="stSidebar"] { 
        z-index: 9998 !important;
        box-shadow: 0 0 50px rgba(0,0,0,.3);
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
        z-index: 9997; 
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
<button class="vb-fab-menu" id="vb-fab-menu" aria-label="Open navigation menu" title="Menu" tabindex="0"></button>
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
    
    // Get DOM elements (with retry for Streamlit's dynamic rendering)
    function getElements() {
        return {
            fab: document.getElementById('vb-fab-menu'),
            hamburger: document.querySelector('[data-testid="stSidebarNavOpen"]'),
            hamburgerBtn: document.querySelector('[data-testid="stSidebarNavOpen"] button'),
            sidebar: document.querySelector('[data-testid="stSidebar"]')
        };
    }
    
    // Open sidebar by clicking native hamburger - ENHANCED VERSION
    function openSidebar(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        const els = getElements();
        
        // Method 1: Click the button directly
        if (els.hamburgerBtn) {
            try {
                els.hamburgerBtn.click();
                console.log('VocalBrand: Sidebar opened via button click');
                return true;
            } catch (err) {
                console.warn('VocalBrand: Button click failed:', err);
            }
        }
        
        // Method 2: Dispatch native events on button
        if (els.hamburgerBtn) {
            try {
                const clickEvent = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                els.hamburgerBtn.dispatchEvent(clickEvent);
                console.log('VocalBrand: Sidebar opened via button event');
                return true;
            } catch (err) {
                console.warn('VocalBrand: Button event failed:', err);
            }
        }
        
        // Method 3: Click the parent container
        if (els.hamburger) {
            try {
                els.hamburger.click();
                console.log('VocalBrand: Sidebar opened via parent click');
                return true;
            } catch (err) {
                console.warn('VocalBrand: Parent click failed:', err);
            }
        }
        
        // Method 4: Directly toggle sidebar visibility (last resort)
        if (els.sidebar) {
            try {
                const currentDisplay = window.getComputedStyle(els.sidebar).display;
                if (currentDisplay === 'none' || els.sidebar.style.transform === 'translateX(-100%)') {
                    els.sidebar.style.display = 'block';
                    els.sidebar.style.transform = 'translateX(0)';
                    els.sidebar.style.visibility = 'visible';
                    console.log('VocalBrand: Sidebar opened via direct style manipulation');
                    return true;
                }
            } catch (err) {
                console.warn('VocalBrand: Direct manipulation failed:', err);
            }
        }
        
        console.error('VocalBrand: All sidebar opening methods failed');
        return false;
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
    
    // Sync FAB button visibility
    function syncFab() {
        const els = getElements();
        if (!els.fab) return;
        
        if (isMobileView()) {
            els.fab.style.display = 'flex';
        } else {
            els.fab.style.display = 'none';
        }
    }
    
    // Main initialization
    function init() {
        const els = getElements();
        
        // Attach FAB click handler with multiple event types
        if (els.fab) {
            // Remove any existing listeners to prevent duplicates
            const newFab = els.fab.cloneNode(true);
            els.fab.parentNode.replaceChild(newFab, els.fab);
            
            // Click event
            newFab.addEventListener('click', function(e) {
                console.log('VocalBrand: FAB clicked');
                openSidebar(e);
            });
            
            // Touch events for better mobile support
            newFab.addEventListener('touchstart', function(e) {
                console.log('VocalBrand: FAB touched');
                e.preventDefault();
                openSidebar(e);
            }, { passive: false });
            
            // Pointer events (modern alternative)
            newFab.addEventListener('pointerdown', function(e) {
                if (e.pointerType === 'touch' || e.pointerType === 'pen') {
                    console.log('VocalBrand: FAB pointer down');
                    openSidebar(e);
                }
            });
            
            console.log('VocalBrand: FAB event listeners attached');
        }
        
        // Initial setup
        enforceHamburgerVisibility();
        syncFab();
        
        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                enforceHamburgerVisibility();
                syncFab();
            }, 200);
        });
        
        // Persistent monitoring to override any CSS that might hide elements
        setInterval(function() {
            enforceHamburgerVisibility();
            syncFab();
        }, CHECK_INTERVAL);
        
        console.log('VocalBrand: Mobile navigation initialized ✓');
    }
    
    // Wait for DOM to be ready, then initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Re-initialize on Streamlit reruns (multiple attempts for reliability)
    setTimeout(init, 100);
    setTimeout(init, 500);
    setTimeout(init, 1000);
    setTimeout(init, 2000); // Extra attempt for slower connections
    
    // Add a visual indicator that FAB is ready (pulse animation)
    setTimeout(function() {
        const fab = document.getElementById('vb-fab-menu');
        if (fab && isMobileView()) {
            fab.classList.add('pulse');
            // Remove pulse after 5 seconds
            setTimeout(function() {
                fab.classList.remove('pulse');
            }, 5000);
        }
    }, 1500);
})();
</script>
    """
    markdown(html, unsafe_allow_html=True)
