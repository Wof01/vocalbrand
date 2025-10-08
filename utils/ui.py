"""UI helpers for VocalBrand Streamlit app."""
from __future__ import annotations
import streamlit as st
from typing import Iterable

SUPREME_CSS = """
<style>
:root { --primary-blue:#1a365d; --accent-gold:#d4af37; }
.main { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); font-family: 'Inter',sans-serif; }
.stApp { background:white; border-radius:20px; box-shadow:0 25px 50px -12px rgba(0,0,0,.25); margin:2rem; min-height:90vh; }
.stButton>button { background:linear-gradient(135deg,var(--primary-blue) 0%, #2d3748 100%); color:white; border:none; padding:.75rem 2rem; border-radius:12px; font-weight:600; font-size:1rem; transition:.3s; }
.stButton>button:hover { transform:translateY(-2px); box-shadow:0 10px 15px -3px rgba(0,0,0,.1); }
.premium-card { background:white; padding:2rem; border-radius:16px; box-shadow:0 10px 25px rgba(0,0,0,.05); border:1px solid #e2e8f0; margin:1rem 0; }
.supreme-header { font-size:2.5rem; font-weight:700; background:linear-gradient(135deg,var(--primary-blue) 0%, var(--accent-gold) 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-align:center; margin-bottom:1rem; }

/* --- Mobile-first navigation reliability --- */
@media (max-width: 992px) {
    /* Keep Streamlit hamburger visible and tappable */
    [data-testid="stSidebarNavOpen"] button,
    [data-testid="stSidebarNavOpen"] svg { opacity: 1 !important; }
    [data-testid="stSidebarNavOpen"] { position: sticky; top: .5rem; z-index: 1000; }
    /* Ensure sidebar overlay sits above content */
    section[data-testid="stSidebar"] { z-index: 1001 !important; }
    /* Enlarge tap target */
    [data-testid="stSidebarNavOpen"] button { width: 44px; height: 44px; }
}

/* --- Elegant step dots / phase transitions --- */
.vb-steps { display:flex; gap:.5rem; align-items:center; justify-content:center; margin: .5rem 0 1rem; }
.vb-step { width:10px; height:10px; border-radius:50%; background:#cbd5e1; transition: transform .2s, background .2s; }
.vb-step.active { background: var(--accent-gold); transform: scale(1.2); box-shadow: 0 0 0 4px rgba(212,175,55,.15); }
.vb-step.done { background:#22c55e; }

/* Keep headers sticky for quick navigation on small screens */
.block-container>div:first-child { position: sticky; top: 0; background: white; z-index: 500; padding-top: .5rem; }

/* Touch-friendly controls */
button, .stButton>button { min-height: 44px; }

/* Subtle card polish */
.vb-card { background:white; border:1px solid #e5e7eb; border-radius:14px; padding:1rem; box-shadow: 0 6px 16px rgba(0,0,0,.06); }

/* Compact status chips */
.vb-chiprow { display:flex; flex-wrap:wrap; gap:.4rem .5rem; }
.vb-chip { display:inline-flex; align-items:center; gap:.35rem; padding:.25rem .55rem; border-radius:999px; font-weight:600; font-size:.8rem; border:1px solid; white-space:nowrap; }
.vb-chip .dot { width:8px; height:8px; border-radius:50%; background:currentColor; opacity:.7; }
.vb-chip.ok { background:#ecfdf5; color:#065f46; border-color:#a7f3d0; }
.vb-chip.warn { background:#fffbeb; color:#92400e; border-color:#fde68a; }
.vb-chip.err { background:#fef2f2; color:#991b1b; border-color:#fecaca; }

/* Sidebar polish: stretch actions and images */
section[data-testid="stSidebar"] .stButton>button { width: 100%; }
section[data-testid="stSidebar"] img { width: 100% !important; height: auto !important; }
section[data-testid="stSidebar"] { padding-right: .5rem; }

/* Slightly tighter spacing in narrow screens */
@media (max-width: 640px) {
    .vb-card { padding: .75rem; }
    .premium-card { padding: 1rem; }
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
