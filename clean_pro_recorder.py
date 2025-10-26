#!/usr/bin/env python
"""Clean up Pro Recorder - remove white artifacts and messy code"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# STEP 1: Remove the aggressive CSS injection block (lines 703-712)
# Replace the entire markdown CSS block with nothing
pattern1 = r'''        # 🎯 SUPREME: Inject aggressive CSS to eliminate white artifacts - TARGET STREAMLIT INTERNALS\n        st\.markdown\(\"""<style>\ndiv\[data-testid="stVerticalBlock"\] > div\[data-testid="stElementContainer"\] \{ margin:0!important; padding:0!important; \}\ndiv\[data-testid="stElementContainer"\] \{ background:transparent!important; margin:0!important; padding:0!important; \}\naudio, canvas \{ margin:0\.25rem 0!important; padding:0!important; background:transparent!important; border:none!important; \}\niframe \{ border:none!important; margin:0!important; padding:0!important; \}\n\.stInfo \{ padding:0\.5rem!important; margin:0!important; background:rgba\(31,41,55,0\.05\)!important; border:1px solid rgba\(156,163,175,0\.2\)!important; \}\ndiv\[data-testid="stInfo"\] \{ margin:0\.25rem 0!important; padding:0\.5rem!important; \}\ndiv\[data-testid="stHorizontalBlock"\] \{ gap:0\.5rem!important; margin:0\.5rem 0!important; padding:0!important; \}\ndiv\[role="status"\] \{ margin:0!important; padding:0!important; \}\n</style>\""", unsafe_allow_html=True\)\n'''
content = re.sub(pattern1, '', content)

# STEP 2: Replace the verbose st.info() with a simple one
pattern2 = r'''        st\.info\(\n            \(\n                "Using Pro Recorder \(live timer \+ waveform\)\\.\\n\\n"\n                "After you stop, the audio bar stays visible here\. Tap 'Use recording' to lock it in and continue\\.\\n\\n"\n                "Tip: If something blocks ingestion, you can also click 'Download recording' and upload it below\."\n            \)\n            if force_pro\n            else \(\n                "Native recorder unavailable: %s\. Using built-in HTML5 fallback \(refresh if permissions denied\)\\.\\n\\n"\n                "After you stop, the audio bar stays visible here\. Tap 'Use recording' to lock it in and continue\\.\\n\\n"\n                "Tip: If something blocks ingestion, you can also click 'Download recording' and upload it below\."\n            \)\n            % \(RECORDER_MSG or "component missing"\),\n            icon="ℹ️",\n        \)'''
replacement = '''        st.info("Pro Recorder ready. Record, then tap the button below.", icon="ℹ️")'''
content = re.sub(pattern2, replacement, content, flags=re.DOTALL)

# STEP 3: Remove the caption and spacing divs (around line 1191-1196)
# Remove: st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
# Remove: st.caption("Pro Recorder provides...")
# Remove: st.markdown("<div style='height:0.5rem;margin-bottom:0.25rem'></div>", unsafe_allow_html=True)
pattern3 = r'''        st\.markdown\("<div style='height:0\.25rem'></div>", unsafe_allow_html=True\)\n        st\.caption\(\n            "Pro Recorder provides live timing \+ waveform\. After stopping, a 'Download recording' link appears; if auto‑ingest doesn't trigger, download and upload the file below to continue\."\n        \)\n        st\.markdown\("<div style='height:0\.5rem;margin-bottom:0\.25rem'></div>", unsafe_allow_html=True\)\n'''
content = re.sub(pattern3, '', content)

# Save the cleaned file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Cleaned Pro Recorder - removed white artifacts and messy code")
