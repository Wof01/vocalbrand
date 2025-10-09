# 🎯 ANNUAL PRO SETUP - EXPLAINED LIKE YOU'RE 5 YEARS OLD

## 🍕 THE PIZZA ANALOGY

**Imagine you love pizza:**
- **Monthly plan** = Buy 1 slice every week for €29 = €348/year total
- **Annual plan** = Buy the whole pizza once for €290 = Save €58!

**Same pizza. Same taste. Just smarter payment.**

---

## 📋 TABLE OF CONTENTS

1. [Quick Setup (5 minutes)](#quick-setup-5-minutes) ← Start here!
2. [Option A: Payment Link (Easiest)](#option-a-payment-link-easiest)
3. [Option B: In-App Button (Supreme)](#option-b-in-app-button-supreme)
4. [Testing](#testing-your-setup)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 QUICK SETUP (5 MINUTES)

### What You Need:
1. Stripe account (you have ✅)
2. Your "VocalBrand Pro" product (you have ✅)
3. 5 minutes of time

### The Goal:
Create an "Annual" price (€290/year) and let customers buy it!

---

## 🟢 OPTION A: PAYMENT LINK (EASIEST)

**Use this if:** You want the simplest solution (recommended!)

### Step 1: Open Stripe Dashboard

1. Go to: [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. **IMPORTANT:** Switch to "Test mode" (toggle at top-right) 🔵
3. Click **"Products"** in left sidebar

### Step 2: Find Your Product

You already created "VocalBrand Pro" - DON'T create a new one!

1. In Products list, click on **"VocalBrand Pro"**
2. You'll see it already has one price: **€29.00/month**

### Step 3: Add Annual Price

Think of this like adding a "combo deal" to your menu!

1. In the product page, find **"Pricing"** section
2. Click **"+ Add another price"** button
3. Fill in the form:
   ```
   Price: 290
   Currency: EUR
   Billing period: Yearly
   ```
4. Click **"Save price"**

🎉 Your product now has TWO prices:
- Monthly: €29
- Yearly: €290

### Step 4: Create Payment Link

Now make a clickable link customers can use!

1. Still on "VocalBrand Pro" page
2. Find your new **"€290.00 per year"** price
3. Click the **three dots (⋮)** next to it
4. Select **"Create payment link"**

### Step 5: Configure the Link

**CRITICAL SETTINGS:**

1. **Quantity**: 
   - Set to **"Fixed quantity"**
   - Value: **1**
   - (So customers can't buy 5 years accidentally!)

2. **Collect customer information**:
   - ✅ Check **"Email addresses"** ← **SUPER IMPORTANT!**
   - (This is how we know WHO bought it!)

3. Click **"Create link"**

4. **COPY THE URL** - looks like:
   ```
   https://buy.stripe.com/test_xxxx123456
   ```

### Step 6: Add to Your App

**For local testing (.env file):**

Open your `.env` file and add this line:
```bash
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/test_YOUR_LINK_HERE
```

**For Streamlit Cloud:**

1. Go to your app settings
2. Find "Secrets" section
3. Add this line:
   ```toml
   ANNUAL_PAYMENT_LINK = "https://buy.stripe.com/test_YOUR_LINK_HERE"
   ```

### Step 7: Restart Your App

```powershell
# Stop the app (Ctrl+C)
# Start it again
streamlit run app.py
```

### Step 8: CHECK IT WORKS!

1. Open your app
2. Log in
3. Look in sidebar → "Upgrade to VocalBrand Pro" section
4. You should see:
   ```
   💎 Subscription Plans
   
   Monthly Pro — Unlimited generations, cancel anytime    [€29/mo]
   
   Annual Pro — Save 17% (€290/year vs €348/year)        [€290/yr →]
   ```

🎉 **DONE! That's Option A!**

---

## 🔵 OPTION B: IN-APP BUTTON (SUPREME!)

**Use this if:** You want TWO buttons in the app (Monthly AND Annual)

This is more professional but requires one extra step.

### Step 1: Get the Annual Price ID

1. Stripe Dashboard → **Products** → **"VocalBrand Pro"**
2. Find the **€290.00 per year** price
3. Look for the **Price ID** - starts with `price_`
4. **COPY IT!** Example: `price_1ABC2DEF3xyz...`

### Step 2: Add Both Price IDs to Environment

You need TWO price IDs now:

**For local testing (.env file):**
```bash
# Monthly price ID (you already have this)
STRIPE_PRICE_ID=price_xxxMonthly123

# Annual price ID (NEW!)
STRIPE_PRICE_ID_ANNUAL=price_yyyAnnual456
```

**For Streamlit Cloud secrets:**
```toml
STRIPE_PRICE_ID = "price_xxxMonthly123"
STRIPE_PRICE_ID_ANNUAL = "price_yyyAnnual456"
```

### Step 3: Restart Your App

```powershell
streamlit run app.py
```

### Step 4: CHECK IT WORKS!

Now you have **TWO REAL BUTTONS**:

```
💎 Subscription Plans

Monthly Pro — Unlimited generations, cancel anytime    [€29/mo]  ← BUTTON
                                                                     (clicks → Stripe checkout)

Annual Pro — Save 17% (€290/year vs €348/year)        [€290/yr] ← BUTTON
                                                                     (clicks → Stripe checkout)
```

Both buttons open Stripe Checkout (not just links)!

🎉 **SUPREME SETUP COMPLETE!**

---

## 🧪 TESTING YOUR SETUP

### Test in Test Mode (Safe!)

**NEVER test with real money!** Always use Stripe Test Mode.

### Test Script:

1. **Make sure test mode is ON** (blue toggle in Stripe)
2. **Create test account** in your app: `test@example.com`
3. **Click "€290/yr" button**
4. Stripe checkout opens
5. **Use test card:** `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/30)
   - CVC: Any 3 digits (e.g., 123)
6. **Complete purchase**
7. **Check:**
   - Webhook logs: `[INFO] Activated subscription for user X`
   - App sidebar: "Subscription: Active 💎"

**Expected:** Subscription activates automatically! ✅

---

## 🎓 WHAT HAPPENS WHEN CUSTOMER CLICKS?

### Option A (Payment Link):
```
Customer clicks "€290/yr →"
    ↓
Opens Stripe Payment Link
    ↓
Customer pays
    ↓
Webhook receives event
    ↓
Detects €290 = Annual subscription
    ↓
Sets subscription_active = 1
    ↓
Customer sees "Subscription: Active 💎"
```

### Option B (In-App Button):
```
Customer clicks "€290/yr" button
    ↓
App calls payment_manager.create_checkout_session(plan="annual")
    ↓
Opens Stripe Checkout with annual price
    ↓
Customer pays
    ↓
Webhook activates subscription
    ↓
Done!
```

**Both are automatic! Both work perfectly!**

---

## 💡 WHY TWO OPTIONS?

| Feature | Option A (Payment Link) | Option B (In-App Button) |
|---------|------------------------|-------------------------|
| **Setup time** | 5 minutes | 7 minutes |
| **Code changes** | Zero | Minimal |
| **Professional look** | Good | Better |
| **Flexibility** | High | Highest |
| **Recommendation** | ⭐ Start here | ⭐⭐ Ultimate |

**My advice:** Start with Option A today, upgrade to Option B tomorrow!

---

## 🔧 TROUBLESHOOTING

### "I don't see the Annual option in my app"

**Check:**
1. ✅ Did you add `ANNUAL_PAYMENT_LINK` to environment?
2. ✅ Did you restart the app after adding it?
3. ✅ Is the value a real URL (starts with `https://`)?

**Fix:**
```bash
# In .env file, make sure you have:
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/test_YOUR_REAL_LINK

# Then restart:
streamlit run app.py
```

### "Customer paid but didn't get activated"

**Most common cause:** Different email addresses!

**Check:**
- VocalBrand account email: `john@company.com`
- Stripe checkout email: `john@gmail.com` ← Different!

**Fix:** Always tell customers:
> **Important:** Use the SAME email address as your VocalBrand account when checking out.

### "Both buttons show Monthly price"

**Cause:** You didn't set `STRIPE_PRICE_ID_ANNUAL`

**Fix:**
```bash
# Add to .env:
STRIPE_PRICE_ID_ANNUAL=price_YOUR_ANNUAL_PRICE_ID
```

Get the price ID from Stripe Dashboard → Products → VocalBrand Pro → find the €290/year price.

---

## 📊 WHICH CUSTOMERS CHOOSE WHAT?

Based on SaaS industry data:

- **Monthly (€29)**: 70% of customers
  - Trying the service
  - Want flexibility
  - Smaller businesses

- **Annual (€290)**: 30% of customers
  - Serious users
  - Want best deal
  - Better cash flow for you!

**Pro tip:** Some customers start Monthly, then switch to Annual later. That's normal!

---

## 💰 YOUR REVENUE COMPARISON

### Scenario 1: Only Monthly
```
100 customers × €29/mo × 12 months = €34,800/year
```

### Scenario 2: Mixed (70% Monthly, 30% Annual)
```
70 customers × €29/mo × 12 = €24,360
30 customers × €290/year  = €8,700
TOTAL = €33,060/year
```

**Wait, that's less?**

**BUT:** You get €8,700 **upfront** in January! Better cash flow!

Plus:
- ✅ Annual customers stay longer (lower churn)
- ✅ Less admin (fewer monthly charges)
- ✅ Predictable revenue

---

## 🎯 BEST PRACTICES

### 1. Show the Savings

**Good:** "Annual Pro — €290/yr"
**Better:** "Annual Pro — Save 17%"
**BEST:** "Annual Pro — Save 17% (€290/year vs €348/year)" ← What you have!

### 2. Position Annual as Premium

Don't hide it! Make it visible:
- Show it RIGHT AFTER monthly
- Use same visual weight
- Make it easy to find

### 3. Test Messaging

Try different words:
- "Save €58 per year"
- "2 months free"
- "Best value"

See what converts better!

### 4. Add Social Proof (Future)

```markdown
**Annual Pro** — Save 17%
⭐ Most popular with agencies
```

---

## 📝 ENVIRONMENT VARIABLES REFERENCE

### Complete Setup (All Options):

```bash
# Core Stripe
STRIPE_API_KEY=sk_test_...               # Your Stripe secret key
STRIPE_PRICE_ID=price_xxxMonthly         # Monthly €29 price ID
STRIPE_PRICE_ID_ANNUAL=price_yyyAnnual   # Annual €290 price ID (OPTIONAL)

# Payment Links (OPTIONAL - for Option A)
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/test_...

# Other
STRIPE_WEBHOOK_SECRET=whsec_...
APP_BASE_URL=http://localhost:8501
```

### Minimal Setup (Just Payment Link):

```bash
STRIPE_API_KEY=sk_test_...
STRIPE_PRICE_ID=price_xxxMonthly
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/test_...
```

That's it! Just 3 variables for Option A!

---

## 🚀 DEPLOYMENT CHECKLIST

### Before Going Live:

- [ ] Annual price created in Stripe (€290/year)
- [ ] Payment Link created (if using Option A)
- [ ] "Collect email addresses" enabled in Payment Link
- [ ] Environment variables added
- [ ] Tested in Test Mode with test card
- [ ] Verified subscription activates automatically
- [ ] Checked sidebar shows "Subscription: Active 💎"
- [ ] Switched to Live Mode
- [ ] Created live prices (same process, live mode)
- [ ] Updated environment with live price IDs/links
- [ ] Tested once more with real card (small amount)
- [ ] Everything works? GO LIVE! 🎉

---

## 🎬 RECAP (TL;DR)

### Option A (Payment Link) - 5 Minutes:
1. Stripe → Products → VocalBrand Pro
2. Add another price → €290, Yearly
3. Create payment link → Enable email collection
4. Copy URL → Add to `ANNUAL_PAYMENT_LINK`
5. Restart app → Done!

### Option B (In-App Button) - 7 Minutes:
1. Do Option A steps 1-2
2. Copy the annual price ID (`price_xxx`)
3. Add to `STRIPE_PRICE_ID_ANNUAL`
4. Restart app → Two buttons appear!

### Testing:
1. Use test mode
2. Test card: 4242 4242 4242 4242
3. Check subscription activates
4. Go live!

---

## 🎁 BONUS: UPSELL STRATEGIES

### During Onboarding:
```
"Welcome! Choose your plan:
 □ Monthly €29/mo
 ☑ Annual €290/yr (Save €58!) ← DEFAULT SELECTED
```

### Email Campaign:
```
Subject: Save 17% with Annual Billing

Hey {{name}},

You're paying €29/month = €348/year.

Switch to annual for €290/year = Save €58!

Plus: One payment, one year of peace of mind.

[Switch to Annual →]
```

### In-App Banner (Future):
```
💡 You could save €58/year with Annual billing! [Upgrade now →]
```

---

## ✅ YOU'RE DONE!

**You now have:**
- ✅ Annual Pro pricing (€290/yr)
- ✅ Automatic activation via webhook
- ✅ Professional UI showing both options
- ✅ 17% discount messaging
- ✅ Complete understanding of how it works

**Deploy and start capturing annual revenue! 🚀**

---

## 🆘 STILL CONFUSED?

### Quick Check:

**Question:** Do I need BOTH Option A and Option B?
**Answer:** NO! Pick ONE:
- Option A = Easiest (Payment Link)
- Option B = Most professional (In-App Button)

**Question:** Will customers automatically get 1 year access?
**Answer:** YES! Webhook handles it automatically.

**Question:** What if they want to upgrade from Monthly to Annual?
**Answer:** They cancel monthly in Stripe, then buy annual. (Or you can help manually)

**Question:** Can I test without real money?
**Answer:** YES! Always use Test Mode first.

---

**Now go make it rain annual subscriptions! 💰💎**
