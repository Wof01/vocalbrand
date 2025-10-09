# VocalBrand — Pricing and Cost Model (Live Ops Guide)

This doc explains how we price, how costs scale with ElevenLabs, and how to configure Stripe without changing app code.

## Current in-app subscription (no code changes)

- Product: `VocalBrand Pro`
- Price (recurring): `Monthly — €29`
- `.env`: set `STRIPE_PRICE_ID` to the Stripe ID of “VocalBrand Pro — Monthly”.

## Payment Links (outside the app UI)

- One-time onboarding:
  - `Setup — Professional` — €497
  - `Setup — Enterprise` — €997
- Optional:
  - `VocalBrand Pro — Annual` — €290
  - Minutes packs (only after confirming your real CPM with ElevenLabs).

### How to surface Payment Links inside the app (optional)

Create the Payment Links in Stripe and set the following environment variables with the full URLs. The app will render them as plain links in the Upgrade section. This does not change any logic or state.

```
SETUP_PRO_PAYMENT_LINK=https://buy.stripe.com/...
SETUP_ENT_PAYMENT_LINK=https://buy.stripe.com/...
PACK60_PAYMENT_LINK=https://buy.stripe.com/...
PACK300_PAYMENT_LINK=https://buy.stripe.com/...
PACK1000_PAYMENT_LINK=https://buy.stripe.com/...
```

These are external one-time purchases; they do not automatically grant in-app entitlements while features are locked.

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
