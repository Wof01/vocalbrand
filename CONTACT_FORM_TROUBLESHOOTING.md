# 🔧 CONTACT FORM TROUBLESHOOTING GUIDE

## 🎯 Quick Diagnosis

**Problem:** Contact form not working?  
**Solution:** Follow this diagnostic tree:

```
┌─ Can you see "Contact" in sidebar?
│
├─ NO → Check app.py imported email_utils ✅
│        Restart app with: streamlit run app.py
│
└─ YES → Click Contact
    │
    ├─ Shows "not configured" message?
    │   │
    │   ├─ YES → Check .env has all 6 variables
    │   │        Restart app
    │   │
    │   └─ NO → Form is visible ✅
    │       │
    │       └─ Fill form and click Send
    │           │
    │           ├─ "Email authentication failed"
    │           │   → Wrong App Password
    │           │   → Solution: Regenerate in Gmail
    │           │
    │           ├─ "Connection refused" / "Connection timeout"
    │           │   → Firewall/network issue
    │           │   → Solution: Check internet, try VPN
    │           │
    │           ├─ "getaddrinfo failed"
    │           │   → DNS issue
    │           │   → Solution: Check internet connection
    │           │
    │           └─ "Message sent successfully!" ✅
    │               → Check Gmail inbox
    │               → If not there, check Spam
```

---

## ❌ ERROR 1: "Contact form is not yet configured"

### What It Means
The app can't find email configuration in environment variables.

### Possible Causes
1. `.env` file not filled
2. Missing one or more variables
3. App not restarted after editing `.env`
4. Using `.env.txt` instead of `.env`

### Solutions

#### Solution A: Check .env File Exists
```powershell
# Check if .env exists
Test-Path .env
# Should return: True

# If False, rename .env.txt to .env:
Rename-Item .env.txt .env
```

#### Solution B: Verify All Variables
Open `.env` and check these 6 lines are filled:
```bash
SMTP_HOST=smtp.gmail.com          # ✅ Must be filled
SMTP_PORT=587                     # ✅ Must be filled
SMTP_USERNAME=your@gmail.com      # ✅ Must be filled
SMTP_PASSWORD=xxxx xxxx xxxx xxxx # ✅ Must be filled
SMTP_FROM_EMAIL=your@gmail.com    # ✅ Must be filled
SUPPORT_EMAIL=your@gmail.com      # ✅ Must be filled
```

#### Solution C: Restart App
```powershell
# Stop app
Ctrl + C

# Start again
streamlit run app.py
```

#### Solution D: Check for Typos
Common mistakes:
- `STMP_HOST` ❌ → `SMTP_HOST` ✅
- `SMTP_USER` ❌ → `SMTP_USERNAME` ✅
- `SMTP_PASS` ❌ → `SMTP_PASSWORD` ✅

---

## ❌ ERROR 2: "Email authentication failed"

### What It Means
Gmail rejected your App Password.

### Possible Causes
1. Wrong App Password
2. 2-Step Verification not enabled
3. App Password revoked
4. Typo in password

### Solutions

#### Solution A: Verify 2-Step Verification
1. Go to: https://myaccount.google.com/security
2. Check "2-Step Verification" shows **ON**
3. If OFF, enable it first

#### Solution B: Regenerate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Click on "VocalBrand" (if exists) → **Delete**
3. Create new:
   - Select app: **Mail**
   - Select device: **Other (Custom)** → "VocalBrand"
   - Click **Generate**
4. **COPY the new password** (16 characters with spaces)
5. Update `.env`:
   ```bash
   SMTP_PASSWORD=abcd efgh ijkl mnop  # New password here
   ```
6. Restart app

#### Solution C: Check for Extra Spaces
```bash
# WRONG (extra spaces)
SMTP_PASSWORD= abcd efgh ijkl mnop

# CORRECT (no leading space)
SMTP_PASSWORD=abcd efgh ijkl mnop
```

#### Solution D: Verify Gmail Account
Make sure `SMTP_USERNAME` is the SAME Gmail account you created App Password for.

```bash
# These must match:
SMTP_USERNAME=john@gmail.com     # ← This account
SMTP_PASSWORD=xxxx xxxx xxxx     # ← App Password from john@gmail.com
```

---

## ❌ ERROR 3: "Failed to send email: [Errno 11001] getaddrinfo failed"

### What It Means
Can't connect to Gmail server (DNS/network issue).

### Possible Causes
1. No internet connection
2. DNS not resolving `smtp.gmail.com`
3. Corporate firewall blocking
4. VPN interfering

### Solutions

#### Solution A: Check Internet
```powershell
# Test Google
ping google.com

# Test Gmail SMTP
ping smtp.gmail.com
```

#### Solution B: Check DNS
```powershell
# Flush DNS cache
ipconfig /flushdns

# Test DNS resolution
nslookup smtp.gmail.com
# Should return: 142.250.X.X
```

#### Solution C: Try Different Network
- Disconnect VPN
- Try mobile hotspot
- Try different WiFi network

#### Solution D: Check Firewall
Corporate firewall might block port 587.
```powershell
# Test port 587
Test-NetConnection -ComputerName smtp.gmail.com -Port 587
# TcpTestSucceeded should be True
```

If blocked, ask IT to allow:
- Domain: `smtp.gmail.com`
- Port: `587` (TLS)
- Protocol: TCP

---

## ❌ ERROR 4: "Connection refused" / "Connection timeout"

### What It Means
Can't connect to Gmail SMTP server on port 587.

### Possible Causes
1. Firewall blocking port 587
2. ISP blocking SMTP
3. Wrong port number

### Solutions

#### Solution A: Verify Port
Check `.env`:
```bash
SMTP_PORT=587  # ✅ Correct for Gmail
# NOT 465, 25, or 2525
```

#### Solution B: Try Alternative Port
Gmail also supports port 465 (SSL):
```bash
SMTP_PORT=465
```
Then update `email_utils.py`:
```python
# Change from:
server.starttls()
# To:
# (port 465 uses SSL by default, no starttls needed)
```

#### Solution C: Check Windows Firewall
```powershell
# Check if port 587 is blocked
Get-NetFirewallRule | Where-Object {$_.LocalPort -eq 587}

# Allow port 587 outbound
New-NetFirewallRule -DisplayName "Gmail SMTP" -Direction Outbound -LocalPort 587 -Protocol TCP -Action Allow
```

#### Solution D: Contact ISP
Some ISPs block SMTP ports. Call them and ask:
- "Do you block outbound port 587?"
- "Can you enable SMTP for my account?"

---

## ❌ ERROR 5: "SMTPServerDisconnected: Connection unexpectedly closed"

### What It Means
Gmail closed connection during authentication.

### Possible Causes
1. Gmail suspicious activity detection
2. Too many failed attempts
3. Account temporarily locked

### Solutions

#### Solution A: Unlock Account
1. Go to: https://accounts.google.com/DisplayUnlockCaptcha
2. Click **"Continue"**
3. Wait 10 minutes
4. Try again

#### Solution B: Allow Less Secure Apps (Workaround)
**Note:** Google deprecated this, but might help temporarily.
1. Go to: https://myaccount.google.com/lesssecureapps
2. Turn ON (if available)
3. Try sending email within 10 minutes

#### Solution C: Check Gmail Activity
1. Go to: https://myaccount.google.com/notifications
2. Look for "Suspicious activity" alerts
3. Click "Yes, it was me" if you see login attempts

---

## ❌ ERROR 6: Email Sent but Not Received

### What It Means
Python says "success" but no email in Gmail.

### Possible Causes
1. Email went to Spam
2. Wrong `SUPPORT_EMAIL`
3. Gmail filter auto-archived it

### Solutions

#### Solution A: Check Spam Folder
```
Gmail → More → Spam
```
If email is there:
1. Click "Not Spam"
2. Add `SMTP_FROM_EMAIL` to contacts
3. Future emails will go to Inbox

#### Solution B: Verify SUPPORT_EMAIL
Check `.env`:
```bash
SMTP_USERNAME=john@gmail.com      # ← Where you send FROM
SUPPORT_EMAIL=john@gmail.com      # ← Where you receive TO
```
These can be different, but make sure `SUPPORT_EMAIL` is correct!

#### Solution C: Check All Mail
```
Gmail → More → All Mail
```
Email might be archived automatically by a filter.

#### Solution D: Check Filters
```
Gmail → Settings ⚙️ → Filters and Blocked Addresses
```
Look for filters that auto-archive emails from yourself.

---

## ❌ ERROR 7: Reply-To Not Working

### What It Means
Clicking "Reply" in Gmail doesn't auto-fill customer's email.

### Possible Causes
1. Email client doesn't support Reply-To header
2. HTML email disabled

### Solutions

#### Solution A: Enable HTML Emails
```
Gmail → Settings ⚙️ → General
→ Find "Enable HTML in emails" → Check it
```

#### Solution B: Manual Reply
1. Open email from contact form
2. Find customer email in body: `Email: customer@example.com`
3. Copy it
4. Compose new email → Paste in "To:" field

#### Solution C: Use Gmail Web (Not App)
Gmail mobile app sometimes doesn't respect Reply-To.
→ Use https://mail.google.com on desktop browser

---

## ❌ ERROR 8: "Please fill in all fields"

### What It Means
Form validation failed - some fields are empty.

### Possible Causes
1. User didn't fill all fields
2. JavaScript disabled
3. Browser compatibility issue

### Solutions

#### Solution A: Fill All Fields
Make sure these are filled:
- ✅ Your Name
- ✅ Your Email
- ✅ Subject
- ✅ Your Message (at least 10 characters)

#### Solution B: Check Browser
Try different browser:
- Chrome ✅ (recommended)
- Firefox ✅
- Edge ✅
- Safari ✅

#### Solution C: Clear Browser Cache
```
Ctrl + Shift + Delete
→ Clear cache and cookies
→ Reload page
```

---

## ❌ ERROR 9: Form Doesn't Submit (Button Does Nothing)

### What It Means
Clicking "Send Message" button has no effect.

### Possible Causes
1. JavaScript error
2. Browser console shows errors
3. Streamlit connection lost

### Solutions

#### Solution A: Check Browser Console
```
Press F12 → Console tab
Look for red errors
```
Common errors:
- WebSocket disconnected → Reload page
- CORS error → Check `APP_BASE_URL` in `.env`

#### Solution B: Reload Page
```
Ctrl + R (Windows)
Cmd + R (Mac)
```

#### Solution C: Check Streamlit Status
Look for red "Not running" banner at top of page.
→ Restart app: `streamlit run app.py`

---

## ❌ ERROR 10: "Please enter a valid email address"

### What It Means
Email format validation failed.

### Possible Causes
1. No `@` in email
2. No `.` after `@`
3. Typo in email

### Solutions

#### Valid Email Formats
```
✅ john@gmail.com
✅ john.smith@company.co.uk
✅ john+test@gmail.com

❌ john@gmail (no .com)
❌ john.gmail.com (no @)
❌ @gmail.com (no username)
```

---

## 🔍 Advanced Debugging

### Enable Debug Logging

Add to `email_utils.py` (top of file):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Restart app and check terminal for detailed logs:
```
INFO:root:Connecting to smtp.gmail.com:587
DEBUG:root:Sending email to support@gmail.com
DEBUG:root:Email sent successfully
```

### Test SMTP Connection Manually

Create `test_smtp.py`:
```python
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

smtp_host = os.getenv("SMTP_HOST")
smtp_port = int(os.getenv("SMTP_PORT", "587"))
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")

print(f"Testing connection to {smtp_host}:{smtp_port}")
print(f"Username: {smtp_username}")

try:
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.set_debuglevel(1)  # Show all SMTP traffic
    server.starttls()
    server.login(smtp_username, smtp_password)
    print("\n✅ SUCCESS! SMTP authentication works!")
    server.quit()
except Exception as e:
    print(f"\n❌ FAILED: {e}")
```

Run it:
```powershell
python test_smtp.py
```

---

## 📊 Error Summary Table

| Error | Cause | Quick Fix |
|-------|-------|-----------|
| "not configured" | Missing `.env` variables | Fill all 6 variables + restart |
| "authentication failed" | Wrong App Password | Regenerate in Gmail |
| "getaddrinfo failed" | No internet/DNS | Check connection |
| "Connection refused" | Port 587 blocked | Check firewall |
| "Connection closed" | Gmail suspicious activity | Unlock at google.com/DisplayUnlockCaptcha |
| Email not received | Spam folder | Check Spam, mark "Not Spam" |
| Reply-To not working | Email client issue | Copy email manually |
| Form won't submit | JavaScript/connection | Reload page |

---

## 🆘 Still Not Working?

### Checklist Before Asking for Help

- [ ] 2-Step Verification enabled in Gmail
- [ ] App Password created and copied correctly
- [ ] All 6 variables in `.env` filled (no typos)
- [ ] App restarted after editing `.env`
- [ ] Internet connection working
- [ ] Tried different browser
- [ ] Checked Spam folder in Gmail
- [ ] Ran `test_smtp.py` (shows detailed error)

### How to Report Issue

Include this info:
```
1. Full error message from app
2. Terminal output (with sensitive info redacted)
3. Output of test_smtp.py
4. Gmail account type (personal/Workspace)
5. OS: Windows/Mac/Linux
6. Browser: Chrome/Firefox/Safari
```

---

**Made with ❤️ by VocalBrand Supreme Team**
