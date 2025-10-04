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
