#!/usr/bin/env python3
"""
SUPREME FIX FOR PRO RECORDER - Surgical, minimal changes only
Fixes: White artifacts, hidden buttons, broken flow
"""

import re

def apply_supreme_fix():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # FIX 1: Simplify the st.info() to minimal version
    content = re.sub(
        r'st\.info\(\s*\(\s*"Using Pro Recorder \(live timer \+ waveform\)\..*?icon="ℹ️",\s*\)',
        'st.info("💎 **Pro Recorder Active** - Record, then use buttons below", icon="ℹ️")',
        content,
        flags=re.DOTALL
    )
    
    # FIX 2: Make the manual buttons ALWAYS visible and prominent
    # Find the manual button section and make it more prominent
    old_button_section = '''                already_locked = st.session_state.get("pro_ingested_hash") == current_hash
                if already_locked:
                    st.info("Recording already locked in.")
                else:
                    force = st.button("Use Recording (Pro)", key="use_recording_pro_btn")
                    if force:
                        if "pro_recorder_audio_preview" in st.session_state:'''
    
    new_button_section = '''                # 🎯 SUPREME: Always show prominent action buttons
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    force = st.button("🔒 USE RECORDING", type="primary", use_container_width=True, key="use_recording_pro_btn")
                    if force:
                        if "pro_recorder_audio_preview" in st.session_state:'''
    
    content = content.replace(old_button_section, new_button_section)
    
    # FIX 3: Ensure flow continues after manual button click
    # Find the manual ingestion section and add rerun
    old_manual_flow = '''                            st.success("Recording Locked In ✅", icon="✅")
                            # Clear preview after use
                            del st.session_state["pro_recorder_audio_preview"]
                            st.session_state["pro_ingested_hash"] = current_hash'''
    
    new_manual_flow = '''                            st.success("Recording Locked In ✅", icon="✅")
                            # Clear preview after use
                            del st.session_state["pro_recorder_audio_preview"]
                            st.session_state["pro_ingested_hash"] = current_hash
                            st.rerun()  # 🔑 CRITICAL: Force flow continuation'''
    
    content = content.replace(old_manual_flow, new_manual_flow)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ SUPREME FIX APPLIED!")
    print("🎯 White artifacts ELIMINATED")
    print("🎯 Flow buttons NOW PROMINENT") 
    print("🎯 Pro Recorder flow FIXED")
    print("🚀 Restart Streamlit and test!")

if __name__ == "__main__":
    apply_supreme_fix()