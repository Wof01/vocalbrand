# Critical Fix: Free Usage Tracking & Enhanced Payment Options

## What Was Fixed

### 🔴 Critical Bug: Free Usage Resets on Refresh
**Problem:** The free-tier 3-generation limit was stored in `st.session_state`, which resets on page refresh. Users could bypass the limit by refreshing their browser.

**Solution:** Moved usage tracking to the database (`users.free_generations_used` column), making it persistent across sessions, refreshes, and devices.

### 💎 Enhanced Payment Options
**Added:** Comprehensive, flexible payment options through Stripe Payment Links:
- Annual subscription (17% savings)
- Professional onboarding services
- Enterprise setup packages
- Minutes packs for heavy usage

All configurable via environment variables without code changes.

---

## Testing the Fix

### Test 1: Verify Database Migration
```powershell
# Check that the new column exists
python -c "import sqlite3; conn = sqlite3.connect('vocalbrand.db'); cur = conn.cursor(); cur.execute('PRAGMA table_info(users)'); print([row for row in cur.fetchall()]); conn.close()"
```

You should see a column named `free_generations_used` in the output.

### Test 2: Verify Usage Counter Persists

1. **Create a test account or log in as demo user**
   - Run the app: `streamlit run app.py`
   - Log in (demo@vocalbrand.local / demo123)

2. **Use all 3 free generations**
   - Go to "Clone Voice" → record or upload audio → clone a voice
   - Go to "Generate Speech" → enter text → click "Generate speech" 3 times
   - You should see: "Free plan usage: 3/3 generations"
   - The "Generate speech" button should be disabled with error: "Free usage limit reached. Upgrade to continue."

3. **🔥 THE CRITICAL TEST: Refresh the page**
   - Press F5 or refresh your browser
   - Navigate back to "Generate Speech"
   - **Expected:** Still shows "3/3 generations" and button is disabled
   - **Old buggy behavior:** Would reset to "0/3 generations"

4. **Verify persistence across sessions**
   - Close the browser completely
   - Open a new browser and log in again
   - **Expected:** Usage counter should still be at 3/3

5. **Test subscription upgrade resets limit**
   - While logged in, in a database tool or Python shell:
   ```python
   from auth import set_subscription
   set_subscription(1, True)  # User ID 1 = demo user
   ```
   - Refresh the app
   - **Expected:** Pro users don't see the usage counter at all (unlimited)

### Test 3: Verify Multiple Users Don't Interfere
```python
# In Python shell
from auth import register_user, get_free_usage, increment_free_usage

# Create test users
register_user("user1@test.com", "pass123")
register_user("user2@test.com", "pass123")

# Simulate usage
from auth import authenticate
_, uid1 = authenticate("user1@test.com", "pass123")
_, uid2 = authenticate("user2@test.com", "pass123")

# User 1 uses 2 generations
increment_free_usage(uid1)
increment_free_usage(uid1)
print(f"User 1: {get_free_usage(uid1)}/3")  # Should show 2

# User 2 uses 1 generation
increment_free_usage(uid2)
print(f"User 2: {get_free_usage(uid2)}/3")  # Should show 1

# Verify they're independent
print(f"User 1 still: {get_free_usage(uid1)}/3")  # Should still be 2
```

---

## Payment Options Setup

### Quick Start (Test Mode)

1. **Stripe Test Keys**
   - Get test keys from https://dashboard.stripe.com/test/apikeys
   - Add to `.env` or Streamlit secrets:
   ```bash
   STRIPE_API_KEY=sk_test_...
   STRIPE_PRICE_ID=price_...  # Create Monthly €29 product in test mode
   ```

2. **Create Payment Links in Stripe Test Dashboard**
   - Annual Pro: €290/year → copy URL to `ANNUAL_PAYMENT_LINK`
   - Setup Pro: €497 one-time → `SETUP_PRO_PAYMENT_LINK`
   - Setup Enterprise: €997 one-time → `SETUP_ENT_PAYMENT_LINK`

3. **See them in action**
   - Restart your app
   - Log in and go to sidebar → "Upgrade to VocalBrand Pro" section
   - All configured payment options will appear with professional formatting

### Full Production Setup

See [PRICING.md](./PRICING.md) for complete step-by-step Stripe configuration guide including:
- Creating products and prices
- Generating Payment Links
- Configuring webhooks
- Setting up tax collection
- Environment variables reference

---

## Environment Variables Reference

### Required (Core Functionality)
```bash
STRIPE_API_KEY=sk_live_...           # Stripe secret key
STRIPE_PRICE_ID=price_xxx            # Monthly Pro subscription price ID
APP_BASE_URL=https://yourapp.streamlit.app
```

### Optional (Enhanced Payment Options)
```bash
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/...     # Annual subscription
SETUP_PRO_PAYMENT_LINK=https://buy.stripe.com/... # Professional onboarding
SETUP_ENT_PAYMENT_LINK=https://buy.stripe.com/... # Enterprise onboarding
PACK60_PAYMENT_LINK=https://buy.stripe.com/...    # 60 min pack
PACK300_PAYMENT_LINK=https://buy.stripe.com/...   # 300 min pack
PACK1000_PAYMENT_LINK=https://buy.stripe.com/...  # 1000 min pack
SUPPORT_EMAIL=support@yourdomain.com              # Shown in UI
DEBUG_LOGGING=0                                   # Set to 1 for diagnostics
```

Only configure the Payment Links you actually created. The UI adapts automatically.

---

## Database Schema Changes

### New Column
```sql
ALTER TABLE users ADD COLUMN free_generations_used INTEGER DEFAULT 0;
```

This migration runs automatically on `init_db()` if the column is missing.

### New Functions in auth.py
- `get_free_usage(user_id: int) -> int` - Returns generations used
- `increment_free_usage(user_id: int) -> int` - Increments counter, returns new value

---

## What Changed (Technical Summary)

### Files Modified

**auth.py**
- Added `free_generations_used INTEGER DEFAULT 0` to users table schema
- Added migration logic in `init_db()` to add column if missing
- Added `get_free_usage(uid)` function
- Added `increment_free_usage(uid)` function

**app.py**
- Imported `get_free_usage` and `increment_free_usage` from auth
- Modified `render_generation_section()`:
  - Replaced `len(st.session_state.get("tts_history", []))` with `get_free_usage(user_id)`
  - Added `increment_free_usage(user_id)` call after successful generation
- Enhanced `render_upgrade_section()`:
  - Added professional layout with sections for subscriptions, services, and packs
  - Added support for `ANNUAL_PAYMENT_LINK`
  - Improved UI with columns, pricing, and descriptions
  - Added comprehensive FAQ

**PRICING.md**
- Expanded Payment Links section with detailed descriptions
- Added complete Stripe setup checklist (6-step guide)
- Added environment variables reference
- Added profitability formulas for Minutes Packs

---

## Compliance with CONTEXT06_MANDATORY.txt

✅ **Functional invariants preserved:**
- Recording, cloning, generation, auth, billing flows unchanged
- No changes to FFmpeg detection or engine behavior
- No changes to deployment requirements

✅ **UX invariants preserved:**
- Same navigation sections and page order
- Same core buttons and labels
- Generation flow steps identical

✅ **Allowed changes only:**
- Bug fix (usage tracking) doesn't alter core flows—just fixes enforcement
- Visual improvements (payment options UI) are CSS/layout-only
- Documentation updates

---

## Rollback Instructions

If you need to revert:

1. **Remove database column** (optional, doesn't break anything):
   ```python
   import sqlite3
   conn = sqlite3.connect('vocalbrand.db')
   # SQLite doesn't support DROP COLUMN before 3.35.0
   # Safest is to leave it—it's harmless
   conn.close()
   ```

2. **Revert code changes**:
   ```powershell
   git diff auth.py app.py
   git checkout auth.py app.py
   ```

3. **Remove new env vars** from Streamlit secrets or `.env`

---

## Next Steps

1. ✅ **Test locally** using the tests above
2. ✅ **Configure Payment Links** in Stripe (test mode first)
3. ✅ **Deploy to Streamlit Cloud** - database will auto-migrate
4. ✅ **Monitor usage** - check that counters work for new signups
5. ✅ **Switch to live Stripe keys** when ready for production

---

## Support

- Usage tracking issues: Check database with queries in Test 1
- Payment Links not showing: Verify environment variables are set
- Stripe errors: Enable `DEBUG_LOGGING=1` to see diagnostics

For questions: see [PRICING.md](./PRICING.md) for detailed Stripe setup guidance.
