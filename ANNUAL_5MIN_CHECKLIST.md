# ⚡ ANNUAL PRO - 5-MINUTE CHECKLIST

Copy this and check off each step as you do it!

---

## 🎯 GOAL
Add Annual subscription (€290/year, save 17%) alongside Monthly (€29/mo)

---

## ✅ CHECKLIST (Option A - Easiest!)

### Step 1: Open Stripe
- [ ] Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
- [ ] Switch to **Test mode** (blue toggle top-right)
- [ ] Click **"Products"** in left sidebar

### Step 2: Find Your Product
- [ ] Click on **"VocalBrand Pro"** (you already made this!)
- [ ] See it has one price: **€29.00 / month**

### Step 3: Add Annual Price
- [ ] Click **"+ Add another price"**
- [ ] Enter: **290**
- [ ] Currency: **EUR**
- [ ] Billing period: **Yearly**
- [ ] Click **"Save price"**
- [ ] ✨ Now you have TWO prices (Monthly + Annual)!

### Step 4: Create Payment Link
- [ ] Find the **€290.00 per year** price
- [ ] Click the **three dots (⋮)** next to it
- [ ] Click **"Create payment link"**
- [ ] Set quantity to **Fixed: 1**
- [ ] ✅ Check **"Email addresses"** under customer info
- [ ] Click **"Create link"**
- [ ] **COPY THE URL** (looks like `https://buy.stripe.com/test_xxx`)

### Step 5: Add to Your App
- [ ] Open your `.env` file
- [ ] Add this line:
  ```bash
  ANNUAL_PAYMENT_LINK=https://buy.stripe.com/test_YOUR_COPIED_URL
  ```
- [ ] Save the file

### Step 6: Restart App
- [ ] Stop your app (Ctrl+C)
- [ ] Start again: `streamlit run app.py`

### Step 7: TEST IT!
- [ ] Open your app: http://localhost:8501
- [ ] Log in
- [ ] Look in sidebar → "Upgrade to VocalBrand Pro"
- [ ] Do you see:
  ```
  Monthly Pro [€29/mo]
  Annual Pro — Save 17% [€290/yr →]
  ```
- [ ] ✅ **IT WORKS!**

---

## 🧪 TEST PURCHASE

- [ ] Click the **"€290/yr →"** link
- [ ] Stripe checkout opens
- [ ] Enter test email: `test@example.com`
- [ ] Card: `4242 4242 4242 4242`
- [ ] Expiry: `12/30` (any future date)
- [ ] CVC: `123` (any 3 digits)
- [ ] Click **"Subscribe"**
- [ ] Back to app → Refresh
- [ ] Sidebar shows: **"Subscription: Active 💎"**
- [ ] ✅ **AUTOMATIC ACTIVATION WORKS!**

---

## 🚀 GO LIVE

Once testing works:

- [ ] Stripe → Switch to **Live mode**
- [ ] Repeat steps 1-4 in Live mode
- [ ] Get NEW live Payment Link URL
- [ ] Update `.env` with LIVE URL
- [ ] Deploy to production
- [ ] ✅ **YOU'RE LIVE!**

---

## 📋 QUICK REFERENCE

**What you created:**
- Monthly Pro: €29/month (existing)
- Annual Pro: €290/year (NEW! 17% savings)

**Customer benefits:**
- Save €58 per year
- Pay once, forget for 12 months
- Same features as monthly

**Your benefits:**
- €290 upfront (better cash flow!)
- Lower churn (annual customers stay longer)
- Professional SaaS pricing

---

## 🆘 HELP

**Don't see Annual option?**
1. Check `.env` has `ANNUAL_PAYMENT_LINK=...`
2. Restart app
3. Refresh browser

**Customer paid but not activated?**
- Check they used SAME email as their account
- Check webhook is running
- See webhook logs for errors

**More help:** See [ANNUAL_SETUP_MEGA_GUIDE.md](./ANNUAL_SETUP_MEGA_GUIDE.md)

---

## ✅ DONE!

- [x] Annual pricing added
- [x] Automatic activation working
- [x] Tested successfully
- [x] Ready to make money!

**Time spent:** 5 minutes  
**Revenue potential:** +30% from annual customers  
**Complexity:** Zero!

🎉 **GO CAPTURE THOSE ANNUAL SUBSCRIPTIONS!** 🎉
