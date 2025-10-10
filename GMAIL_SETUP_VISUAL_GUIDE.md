# 🎯 GMAIL SETUP - VISUAL STEP-BY-STEP

## 📍 STEP 1: Enable 2-Step Verification

### Go to Google Account Security
👉 **URL:** https://myaccount.google.com/security

```
┌─────────────────────────────────────────────┐
│  Google Account                             │
├─────────────────────────────────────────────┤
│                                             │
│  🔒 Security                               │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Signing in to Google                  │ │
│  ├───────────────────────────────────────┤ │
│  │ Password          ●●●●●●●●  ✏️         │ │
│  │                                       │ │
│  │ 2-Step Verification   ⚠️ OFF         │ │ ← CLICK HERE!
│  │ Add an extra layer...  [>]           │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Turn It ON
```
┌─────────────────────────────────────────────┐
│  Set up 2-Step Verification                 │
├─────────────────────────────────────────────┤
│  Add an extra layer of security             │
│                                             │
│  1. Enter your password                     │
│     [●●●●●●●●●●●●]                          │
│                                             │
│  2. Choose verification method:             │
│     ⦿ Text message                         │
│     ○ Phone call                           │
│     ○ Google prompt                        │
│                                             │
│     [ Get Started ]                        │ ← CLICK!
└─────────────────────────────────────────────┘
```

### Verify Your Phone
```
┌─────────────────────────────────────────────┐
│  Enter your phone number                    │
├─────────────────────────────────────────────┤
│  +351 [___________]  🇵🇹                    │
│                                             │
│     [ Send ]                               │ ← CLICK!
└─────────────────────────────────────────────┘

↓ You receive SMS with code

┌─────────────────────────────────────────────┐
│  Enter the code                             │
├─────────────────────────────────────────────┤
│  [G-123456]                                 │
│                                             │
│     [ Verify ]                             │ ← CLICK!
└─────────────────────────────────────────────┘
```

✅ **DONE!** 2-Step Verification is now ON!

---

## 📍 STEP 2: Create App Password

### Go to App Passwords
👉 **URL:** https://myaccount.google.com/apppasswords

```
┌─────────────────────────────────────────────┐
│  App passwords                              │
├─────────────────────────────────────────────┤
│  Use app passwords to sign in to your      │
│  Google Account from apps that don't       │
│  support 2-Step Verification.              │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Select app          [Mail ▼]         │ │ ← SELECT "Mail"
│  │                                       │ │
│  │ Select device       [Other ▼]        │ │ ← SELECT "Other"
│  │                                       │ │
│  │ Name: [VocalBrand_________]          │ │ ← TYPE "VocalBrand"
│  │                                       │ │
│  │     [ Generate ]                     │ │ ← CLICK!
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Copy the Generated Password
```
┌─────────────────────────────────────────────┐
│  Your app password for VocalBrand           │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │                                       │ │
│  │    abcd efgh ijkl mnop               │ │ ← COPY THIS!
│  │                                       │ │
│  │         📋 [Copy]                     │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ⚠️ You won't be able to see this again!   │
│                                             │
│     [ Done ]                               │
└─────────────────────────────────────────────┘
```

**⚠️ IMPORTANT:** Save this password NOW! You can't see it again!

---

## 📍 STEP 3: Fill .env File

### Open .env in VS Code
```
c:\Users\UTILIZADOR\Desktop\MY_APP_2025\...\VOCALBRAND\.env
```

### Find Email Section (around line 8-13)
```python
# ============================================
# EMAIL CONFIGURATION (Contact Form)
# ============================================
SMTP_HOST=smtp.gmail.com            # ← Already filled! ✅
SMTP_PORT=587                       # ← Already filled! ✅
SMTP_USERNAME=                      # ← FILL YOUR GMAIL HERE
SMTP_PASSWORD=                      # ← PASTE APP PASSWORD HERE
SMTP_FROM_EMAIL=                    # ← FILL YOUR GMAIL HERE
SUPPORT_EMAIL=                      # ← FILL YOUR GMAIL HERE
```

### Example (YOUR VALUES):
```python
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=john.vocalbrand@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM_EMAIL=john.vocalbrand@gmail.com
SUPPORT_EMAIL=john.vocalbrand@gmail.com
```

### Save File
```
Ctrl + S  (Windows)
Cmd + S   (Mac)
```

---

## 📍 STEP 4: Restart App

### PowerShell Terminal in VS Code
```
Terminal → New Terminal
```

### Stop Current App
```powershell
# Press Ctrl+C to stop running app
^C
```

### Start App Again
```powershell
streamlit run app.py
```

### You Should See:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.X:8501
```

---

## 📍 STEP 5: Test Contact Form

### Open App
```
http://localhost:8501
```

### Login (or create account)
```
┌─────────────────────────────────────────────┐
│  🎙️ VocalBrand Supreme Console             │
├─────────────────────────────────────────────┤
│  Sidebar:                                   │
│    • Onboarding                            │
│    • Clone Voice                           │
│    • Generate Speech                       │
│    • Contact          ← CLICK HERE!       │
└─────────────────────────────────────────────┘
```

### Fill Contact Form
```
┌─────────────────────────────────────────────┐
│  📧 Contact Us                              │
├─────────────────────────────────────────────┤
│  Your Name *                                │
│  [Test User________________]                │
│                                             │
│  Your Email *                               │
│  [test@example.com_________]                │
│                                             │
│  Subject *                                  │
│  [Testing contact form_____]                │
│                                             │
│  Your Message *                             │
│  ┌─────────────────────────────────────┐   │
│  │This is a test message to verify    │   │
│  │the contact form works perfectly!   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│     [📨 Send Message]  ← CLICK!            │
└─────────────────────────────────────────────┘
```

### You'll See:
```
┌─────────────────────────────────────────────┐
│  ⏳ Sending your message...                 │
└─────────────────────────────────────────────┘

↓ After 1-2 seconds

┌─────────────────────────────────────────────┐
│  ✅ Message sent successfully!              │
│  We'll get back to you soon.               │
│                                             │
│  🎈🎈🎈 (balloons animation)                │
└─────────────────────────────────────────────┘
```

---

## 📍 STEP 6: Check Gmail

### Open Gmail
👉 **URL:** https://mail.google.com

### Look for New Email
```
┌─────────────────────────────────────────────┐
│  Gmail                                      │
├─────────────────────────────────────────────┤
│  📩 Inbox (1)                               │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ VocalBrand Contact: Testing...       │ │ ← YOUR MESSAGE!
│  │ From: john.vocalbrand@gmail.com      │ │
│  │ To: john.vocalbrand@gmail.com        │ │
│  │ Just now                             │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Open Email
```
┌─────────────────────────────────────────────┐
│  VocalBrand Contact: Testing contact form   │
├─────────────────────────────────────────────┤
│  From: john.vocalbrand@gmail.com           │
│  To: john.vocalbrand@gmail.com             │
│  Reply-To: test@example.com                │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ New Contact Form Submission          │ │
│  ├───────────────────────────────────────┤ │
│  │ From: Test User                      │ │
│  │ Email: test@example.com              │ │
│  │ Subject: Testing contact form        │ │
│  ├───────────────────────────────────────┤ │
│  │ Message:                             │ │
│  │ This is a test message to verify     │ │
│  │ the contact form works perfectly!    │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [ Reply ]  [ Forward ]                    │ ← CLICK REPLY!
└─────────────────────────────────────────────┘
```

### Reply to Customer
```
┌─────────────────────────────────────────────┐
│  Reply                                      │
├─────────────────────────────────────────────┤
│  To: test@example.com    ← Auto-filled! ✅ │
│                                             │
│  Hi Test User,                              │
│                                             │
│  Thanks for your message! The contact       │
│  form is working perfectly.                 │
│                                             │
│  Best regards,                              │
│  VocalBrand Support                         │
│                                             │
│     [ Send ]                               │ ← CLICK!
└─────────────────────────────────────────────┘
```

✅ **DONE!** Customer receives your reply instantly!

---

## 🎯 Visual Summary

```
STEP 1: Enable 2-Step
┌──────────────────┐
│ Google Account   │
│ → Security       │
│ → 2-Step ON      │
└──────────────────┘
         ↓
STEP 2: Create App Password
┌──────────────────┐
│ App Passwords    │
│ → Mail → Other   │
│ → Copy password  │
└──────────────────┘
         ↓
STEP 3: Fill .env
┌──────────────────┐
│ SMTP_USERNAME    │
│ SMTP_PASSWORD    │
│ SMTP_FROM_EMAIL  │
│ SUPPORT_EMAIL    │
└──────────────────┘
         ↓
STEP 4: Restart App
┌──────────────────┐
│ Ctrl+C (stop)    │
│ streamlit run    │
└──────────────────┘
         ↓
STEP 5: Test Form
┌──────────────────┐
│ Contact page     │
│ Fill → Send      │
└──────────────────┘
         ↓
STEP 6: Check Gmail
┌──────────────────┐
│ Inbox → Email    │
│ Reply → Send     │
└──────────────────┘
         ↓
       ✅ DONE!
```

---

## 🆘 Can't Find Something?

### "I don't see 2-Step Verification option"
→ Make sure you're logged into the correct Gmail account
→ URL: https://myaccount.google.com/security

### "I don't see App Passwords option"
→ You must enable 2-Step Verification FIRST
→ Refresh the page after enabling 2-Step

### "Which .env file do I edit?"
→ The one in your project root:
```
c:\Users\UTILIZADOR\Desktop\MY_APP_2025\
JEWEL2_VOICE_CLONE_SAAS_FOR_SMALL_BUSINESSES\
VOCALBRAND\.env
```
→ NOT `.env.txt` (that's a template)

### "Contact page shows 'not configured'"
→ Check ALL 6 variables are filled in `.env`
→ Restart the app (Ctrl+C then `streamlit run app.py`)
→ Check for typos in variable names

---

## 💡 Quick Tips

✅ **Use same email for all 3 variables** (simplest)
✅ **Copy-paste App Password** (don't type manually)
✅ **Test in Gmail first** (send test before going live)
✅ **Keep App Password secret** (treat like a password)

---

**Total Time: 5 Minutes ⏱️**
**Cost: $0 💰**
**Difficulty: Easy 🟢**

**Made with ❤️ by VocalBrand Supreme Team**
