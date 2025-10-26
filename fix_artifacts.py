#!/usr/bin/env python
"""
SURGICAL FIX: Remove white artifacts and simplify Pro Recorder flow
- Remove aggressive CSS injection
- Remove verbose st.info() block
- Remove caption and spacing divs
- Keep only the essential Pro Recorder component
"""

import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and remove the section from the st.markdown CSS to the st.info() block
output = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # SKIP the entire CSS injection block (starting with "# 🎯 SUPREME:" comment)
    if "# 🎯 SUPREME: Inject aggressive CSS" in line:
        # Skip until we find the closing of st.info()
        paren_count = 0
        while i < len(lines):
            if "st.info(" in lines[i]:
                paren_count += lines[i].count("(") - lines[i].count(")")
            else:
                paren_count += lines[i].count("(") - lines[i].count(")")
            
            if paren_count == 0 and i > 0 and lines[i].strip().endswith(")"):
                i += 1
                break
            i += 1
        continue
    
    # SKIP the caption and spacing divs after pro_component_val assignment
    elif 'st.markdown("""<div style=\'height:0.25rem\'>' in line or \
         'st.caption(\n            "Pro Recorder provides' in line or \
         'st.markdown("<div style=\'height:0.5rem;margin-bottom:0.25rem\'>' in line:
        # Skip these lines
        if 'st.markdown("""<div style=\'height:0.25rem\'>' in line:
            i += 1  # Skip this line
        elif 'st.caption(' in line:
            # Skip caption and its closing paren (might be multi-line)
            while i < len(lines) and ')' not in lines[i]:
                i += 1
            i += 1
        elif 'st.markdown("<div style=\'height:0.5rem;' in line:
            i += 1
        continue
    
    # SKIP the textarea styling that's causing white artifacts
    elif 'st.markdown("""<style>' in line and 'textarea[key="pro_recorder_payload"]' in ''.join(lines[i:i+10]):
        # Skip the entire style block
        while i < len(lines) and '""", unsafe_allow_html=True)' not in lines[i]:
            i += 1
        i += 1
        continue
    
    output.append(line)
    i += 1

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("✅ Fixed: Removed white artifacts, CSS cruft, and messy UI code")
