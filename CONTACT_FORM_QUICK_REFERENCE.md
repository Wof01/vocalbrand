# 📋 CONTACT FORM - QUICK REFERENCE

## ⚡ What You Need to Fill in .env

Copy these 6 lines to your `.env` file:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=YOUR_GMAIL@gmail.com
SMTP_PASSWORD=YOUR_APP_PASSWORD_16_CHARS
SMTP_FROM_EMAIL=YOUR_GMAIL@gmail.com
SUPPORT_EMAIL=YOUR_GMAIL@gmail.com
```

---

## 🔑 Where to Get Values

| Variable | What It Is | Where to Get It |
|----------|-----------|-----------------|
| `SMTP_HOST` | Gmail server | **Use:** `smtp.gmail.com` (don't change) |
| `SMTP_PORT` | Port number | **Use:** `587` (don't change) |
| `SMTP_USERNAME` | Your Gmail | **Example:** `john@gmail.com` |
| `SMTP_PASSWORD` | App Password | **Get it:** https://myaccount.google.com/apppasswords |
| `SMTP_FROM_EMAIL` | Sender email | **Use:** Same as `SMTP_USERNAME` |
| `SUPPORT_EMAIL` | Where messages go | **Use:** Same as `SMTP_USERNAME` |

---

## 🎯 3-Step Setup

### 1️⃣ Enable 2-Step Verification
👉 https://myaccount.google.com/security
- Click "2-Step Verification"
- Turn it ON

### 2️⃣ Create App Password
👉 https://myaccount.google.com/apppasswords
- Select: Mail → Other (custom) → "VocalBrand"
- Click Generate
- **COPY the 16-character password!**

### 3️⃣ Fill .env and Restart
```bash
# Fill the 6 variables above
# Then restart:
streamlit run app.py
```

---

## ✅ Test Checklist

- [ ] 2-Step Verification enabled
- [ ] App Password created and copied
- [ ] All 6 variables filled in `.env`
- [ ] App restarted
- [ ] Navigate to "Contact" page
- [ ] Send test message
- [ ] Check Gmail inbox for message

---

## 🆘 Quick Fixes

**"Email authentication failed"**
→ Check App Password is correct (regenerate if needed)

**"Contact form is not yet configured"**
→ Check `.env` has all 6 variables filled

**"Connection refused"**
→ Check internet connection and port 587 not blocked

---

## 💡 Pro Tips

✅ **Use same Gmail for all 3 email variables** (simplest setup)
✅ **Test in Gmail first** before going live
✅ **Keep App Password secret** (never commit to GitHub)
✅ **Rotate password every 6 months** for security

---

**Need detailed help?** → See `CONTACT_FORM_SETUP.md`
