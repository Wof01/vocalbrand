# 🎯 TIKTOK BROWSER FIX - QUICK REFERENCE

## 📍 LOCATION
**File:** `utils/ui.py`  
**Function:** `inject_tiktok_browser_fix()`  
**Lines:** 3292-3802  
**Called From:** `inject_css()` function (line ~2260)

## 🔍 WHAT IT DOES
Detects TikTok's in-app browser and shows a branded warning modal explaining that microphone access is blocked, with instructions to open the page in a standard browser.

## 🎯 HOW IT WORKS
1. **Detects TikTok:** Checks user agent for `TikTok` or `musical_ly`
2. **Shows Warning:** Full-screen modal with VocalBrand branding
3. **Provides Solution:** "Open in Browser" button + manual instructions
4. **Logs Details:** Console logs for debugging
5. **Remembers Dismissal:** Uses session storage to avoid nagging

## ✅ AFFECTED BROWSERS
- **TikTok iOS:** Shows warning
- **TikTok Android:** Shows warning
- **All Other Browsers:** No warning (invisible)

## 🚀 TESTING LOCALLY

### Simulate TikTok in Chrome DevTools:
1. Open DevTools (F12)
2. Open Network Conditions (3 dots → More tools → Network conditions)
3. Uncheck "Use browser default"
4. Paste this User Agent:
```
Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TikTok/12.3.0
```
5. Refresh page - warning should appear!

## 📝 CONSOLE LOGS TO LOOK FOR
```
🎯 VocalBrand: TikTok in-app browser detected
🎯 VocalBrand: User Agent: [...]
🎯 VocalBrand: Testing microphone access in TikTok browser...
🎯 VocalBrand: ❌ Microphone access BLOCKED in TikTok
🎯 VocalBrand: TikTok warning displayed
```

## ⚠️ QUICK DISABLE (If Needed)
1. Open `utils/ui.py`
2. Go to `inject_css()` function (~line 2260)
3. Comment out: `# inject_tiktok_browser_fix()`
4. Save and redeploy

## 🔧 CUSTOMIZATION POINTS

### Change Warning Text:
- Edit `.vb-tiktok-title` content (line ~3330)
- Edit `.vb-tiktok-message` content (line ~3331)

### Change Colors:
- Primary button gradient (line ~3414)
- Modal background color (line ~3344)

### Change Timing:
- Modal delay: `setTimeout(showTikTokWarning, 500)` (line ~3660)

## 📊 KEY FEATURES
✅ Detects iOS and Android TikTok  
✅ VocalBrand-branded modal design  
✅ "Open in Browser" button with 3 fallback methods  
✅ Manual instructions for iOS and Android  
✅ Session storage prevents re-showing  
✅ Console logging for debugging  
✅ Zero impact on other browsers  
✅ Mobile-optimized responsive design  
✅ Smooth animations (fade, slide, pulse)  
✅ Maximum z-index for visibility  

## 🐛 COMMON ISSUES

**Q: Warning doesn't appear in TikTok**  
A: Check console - TikTok may have changed user agent

**Q: "Open in Browser" doesn't work**  
A: Expected - manual instructions are the fallback

**Q: Warning appears in Chrome/Safari**  
A: Check user agent - shouldn't contain "TikTok"

**Q: Warning keeps appearing after dismissal**  
A: Expected on refresh - session storage resets

## 📞 MAINTENANCE NOTES
- **No Python modifications** - Pure HTML/CSS/JS
- **Easy to disable** - Just comment out function call
- **Easy to remove** - Delete function + call
- **No database changes** - Client-side only
- **No API calls** - Fully self-contained

## 🎉 SUCCESS INDICATORS
- Users can access recording in standard browsers
- Reduced "microphone doesn't work" complaints
- Clear guidance provided to TikTok users
- All other browsers work normally

---

**Status:** ✅ Production-Ready  
**Impact:** TikTok users only  
**Risk:** Zero (graceful degradation)  
**Rollback:** Simple (comment out 1 line)
