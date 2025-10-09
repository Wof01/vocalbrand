# VocalBrand — Pricing and Cost Model (Live Ops Guide)

This doc explains how we price, how costs scale with ElevenLabs, an## Stripe setup checklist

### Step 1: Create subscription products

**Monthly Pro (required for in-app)**
1. Stripe Dashboard → Products → Create product
2. Name: "VocalBrand Pro"
3. Add recurring price: €29, Monthly, EUR
4. Copy the `price_xxx` ID
5. Set in environment: `STRIPE_PRICE_ID=price_xxx`

**Annual Pro (optional Payment Link)**
1. Same product "VocalBrand Pro"
2. Add second price: €290, Yearly, EUR
3. Create Payment Link for this price
4. Copy the full URL: `https://buy.stripe.com/...`
5. Set in environment: `ANNUAL_PAYMENT_LINK=https://buy.stripe.com/...`

### Step 2: Create one-time service products

**Setup — Professional**
1. Stripe Dashboard → Products → Create product
2. Name: "Setup — Professional"
3. Add one-time price: €497, EUR
4. Create Payment Link → quantity fixed to 1
5. Copy URL, set: `SETUP_PRO_PAYMENT_LINK=https://buy.stripe.com/...`

**Setup — Enterprise**
1. Create product "Setup — Enterprise"
2. One-time price: €997, EUR
3. Create Payment Link → quantity fixed to 1
4. Set: `SETUP_ENT_PAYMENT_LINK=https://buy.stripe.com/...`

### Step 3: Create Minutes Packs (only if profitable)

Calculate profitable pricing first using the formula in the Cost Model section.

**Voice Minutes Pack X**
1. Create product: "Voice Minutes Pack 60" (or 300, 1000)
2. One-time price based on formula
3. Create Payment Link
4. Set: `PACK60_PAYMENT_LINK=https://buy.stripe.com/...` (and similar for 300/1000)

### Step 4: Configure environment variables

Add to your `.env` file or Streamlit Cloud secrets:

```bash
# Core Stripe
STRIPE_API_KEY=sk_live_...  # or sk_test_... for testing
STRIPE_PRICE_ID=price_xxx   # Monthly Pro price ID (required)
STRIPE_WEBHOOK_SECRET=whsec_...  # For webhook verification
APP_BASE_URL=https://yourapp.streamlit.app  # Your app URL

# Optional Payment Links (add only what you created)
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/...
SETUP_PRO_PAYMENT_LINK=https://buy.stripe.com/...
SETUP_ENT_PAYMENT_LINK=https://buy.stripe.com/...
PACK60_PAYMENT_LINK=https://buy.stripe.com/...
PACK300_PAYMENT_LINK=https://buy.stripe.com/...
PACK1000_PAYMENT_LINK=https://buy.stripe.com/...

# Optional
SUPPORT_EMAIL=support@yourdomain.com
DEBUG_LOGGING=0  # Set to 1 for diagnostics
```

### Step 5: Enable Stripe features

- **Automatic tax**: Dashboard → Tax → Enable (for VAT/sales tax)
- **Payment methods**: Enable Cards, Apple Pay, Google Pay
- **Customer portal**: Settings → Billing → Enable (for self-service cancellation)
- **Webhooks**: Add endpoint for `checkout.session.completed` and `customer.subscription.updated`

### Step 6: Test before going live

1. Use test mode keys (`sk_test_...` and test Payment Links)
2. Create test account in app
3. Verify Monthly subscription flow works
4. Test Payment Links open correctly
5. Verify webhook activates subscription in DB
6. Switch to live keys when ready configure Stripe without changing app code.

## Current in-app subscription (no code changes)

- Product: `VocalBrand Pro`
- Price (recurring): `Monthly — €29`
- `.env`: set `STRIPE_PRICE_ID` to the Stripe ID of “VocalBrand Pro — Monthly”.

## Payment Links (outside the app UI)

VocalBrand supports multiple flexible payment options via Stripe Payment Links. These are hosted checkout pages that don't require code changes.

### Subscription Plans

**Monthly Pro (in-app)** — €29/month
- Managed via `STRIPE_PRICE_ID` environment variable
- Users click "Start premium subscription" button in app
- Automatic recurring billing
- Cancel anytime

**Annual Pro (Payment Link)** — €290/year  
- Save 17% vs monthly (€290 vs €348/year)
- Create as Payment Link in Stripe
- Set `ANNUAL_PAYMENT_LINK` environment variable
- Shows in app upgrade section when configured

### One-time Professional Services

**Setup — Professional** — €497
- 60-minute guided onboarding session
- Best for solo entrepreneurs and small teams
- Video call + Q&A + implementation guidance
- Create Payment Link, set `SETUP_PRO_PAYMENT_LINK`

**Setup — Enterprise** — €997
- 120-minute guided onboarding (can split into 2 sessions)
- Best for agencies and larger teams
- Priority support + custom workflow integration
- Create Payment Link, set `SETUP_ENT_PAYMENT_LINK`

### Minutes Packs (Optional)

Only offer these after confirming your ElevenLabs CPM pricing makes them profitable.

**Voice Minutes Pack 60** — €9
- Set `PACK60_PAYMENT_LINK`
- Minimum profitable price depends on your ElevenLabs rate (see formula below)

**Voice Minutes Pack 300** — €39
- Set `PACK300_PAYMENT_LINK`

**Voice Minutes Pack 1000** — €99
- Set `PACK1000_PAYMENT_LINK`

### How to surface Payment Links inside the app

Create the Payment Links in Stripe Dashboard and set environment variables with full URLs:

```bash
# Subscriptions
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/...

# Professional Services
SETUP_PRO_PAYMENT_LINK=https://buy.stripe.com/...
SETUP_ENT_PAYMENT_LINK=https://buy.stripe.com/...

# Minutes Packs (optional - verify profitability first)
PACK60_PAYMENT_LINK=https://buy.stripe.com/...
PACK300_PAYMENT_LINK=https://buy.stripe.com/...
PACK1000_PAYMENT_LINK=https://buy.stripe.com/...
```

The app automatically displays configured links in the Upgrade section with professional formatting. These are visual-only (no code changes) and don't automatically grant in-app entitlements.

## Included usage policy (not enforced in code)

- Pro includes 30 TTS minutes / month.
- Additional usage via Minutes Packs (sold by Payment Link). Keep these profitable using the formula below.

## Cost model

Let:
- `P` = ElevenLabs price per 1,000 characters (from your ElevenLabs billing).
- `CPM` = Cost per minute ≈ `1.4 × P` (1 minute speech ~ 1,400 chars on average English content).
- Stripe fee estimate (to be safe): `2.9% + €0.30` per charge (adjust per your region).

Example with `P = €0.30`:
- `CPM = 1.4 × 0.30 = €0.42/min`.

### Plan economics (example)

Pro `€29` includes `30 min`:
- COGS: `30 × 0.42 = €12.60`
- Stripe fee: `29×0.029 + 0.30 ≈ €1.14`
- Net receipts: `€27.86`
- Gross margin (before infra/support): `€27.86 − €12.60 ≈ €15.26`.

### Minutes Pack pricing formula

Given target margin `M` (e.g., `70%`), minutes `X`, and `CPM`:
- `Pack price ≥ (X × CPM) / (1 − M)`.

Example with `P=€0.30`, `CPM=€0.42`, `M=70%`:
- Pack 60 minimum: `(60×0.42)/0.30 = €84.00`.

If your packs seem high vs. market, renegotiate your ElevenLabs rate or reduce included minutes in base plans.

## Scaling scenarios (example at P=€0.30 → CPM=€0.42)

- 100 Pro subscribers:
  - Revenue: `€2,900`
  - COGS: `100 × 30 × 0.42 = €1,260`
  - Stripe fees (approx): `€114`
  - Gross margin (pre-infra): `€1,526`.

- 500 Pro subscribers:
  - Revenue: `€14,500`
  - COGS: `€6,300`
  - Stripe fees: `€570`
  - Gross margin: `€7,630`.

> Replace `P` with your actual ElevenLabs rate to re-run these numbers.

## Stripe setup checklist

- Create “VocalBrand Pro — Monthly €29” (copy the `price_...` into `.env: STRIPE_PRICE_ID`).
- Create Payment Links: Setup — Professional (€497), Setup — Enterprise (€997).
- Optional: “VocalBrand Pro — Annual €290” Payment Link.
- Enable automatic tax calculation if applicable.
- Enable Apple Pay / Google Pay.
- Keep quantity fixed to 1 for subscriptions.

## Notes

- We keep one in-app price to avoid code changes. Multi-tier inside the app can be added later.
- Minutes are a policy today; enforcement requires future metering (out of scope while features are locked).
- Use DEBUG_LOGGING=`1` for internal diagnostics; keep it `0` in production.
