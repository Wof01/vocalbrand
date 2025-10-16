# 🎯 WHITE ARTIFACT FIX - QUICK REFERENCE

## 📍 LOCATION
**File:** `utils/ui.py`  
**Lines:** 1973-2040  
**Section:** Inside `SUPREME_CSS` constant, before closing `</style>` tag

## 🔍 WHAT IT FIXES
Eliminates white rectangular boxes/backgrounds appearing on:
- Info/instruction boxes
- File upload sections
- Error/success messages
- CTA banners
- Contact page headers
- Recording interfaces
- Audio players

## 🎯 HOW IT WORKS
Uses CSS `background: transparent !important;` to override Streamlit's default white backgrounds on specific elements.

## ✅ SAFE REMOVAL
If you need to remove these rules:
1. Open `utils/ui.py`
2. Find the section marked `/* WHITE ARTIFACT ELIMINATION RULES */`
3. Delete lines 1973-2040 (the entire block)
4. Keep everything else intact

## 🚀 NO RESTART NEEDED
Changes apply immediately when Streamlit auto-reloads. Just save the file.

## ⚠️ DO NOT MODIFY
These rules are surgical fixes. Modifying them may re-introduce white artifacts.

## 📝 MAINTENANCE NOTE
If new white artifacts appear in future features, add similar rules following the same pattern:
```css
/* 🎯 WHITE ARTIFACT FIX #11: [Description] */
[SPECIFIC_SELECTOR] {
    background: transparent !important;
    background-color: transparent !important;
}
```
