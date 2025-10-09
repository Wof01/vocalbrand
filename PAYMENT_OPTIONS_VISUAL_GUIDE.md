# Payment Options UI - Visual Reference

## How It Looks in the App

When you configure Payment Links via environment variables, the sidebar "Upgrade" section transforms from a single button into a comprehensive pricing page with organized sections.

### Section 1: Subscription Plans 💎

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 Subscription Plans
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Monthly Pro — Unlimited generations, cancel anytime          [€29/mo →]

Annual Pro — Save 17% (€290/year vs €348/year)              [€290/yr →]
```

### Section 2: Professional Onboarding 🚀

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Professional Onboarding
One-time guided setup services for teams and enterprises
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Setup — Professional — 60 min guided setup & Q&A             [€497 →]

Setup — Enterprise — 120 min guided setup & Q&A              [€997 →]
```

### Section 3: Additional Minutes Packs ⚡

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Additional Minutes Packs
Premium voice minutes for professional use cases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Voice Minutes Pack 60 min                                    [€89 →]

Voice Minutes Pack 300 min                                   [€399 →]

Voice Minutes Pack 1000 min                                  [€1,299 →]
```

### Section 4: FAQ 💡

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Payment Options FAQ [▼]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

(Expandable section with detailed explanations of each option)
```

---

## Configuration Examples

### Minimal Setup (Just Monthly Subscription)
```bash
# Only required variable
STRIPE_PRICE_ID=price_xxxMonthlyPro
```

**Result:** Shows only the "€29/mo" button (existing behavior)

---

### Recommended Setup (Subscriptions + Services)
```bash
STRIPE_PRICE_ID=price_xxxMonthlyPro
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/test_annual
SETUP_PRO_PAYMENT_LINK=https://buy.stripe.com/test_setup_pro
SETUP_ENT_PAYMENT_LINK=https://buy.stripe.com/test_setup_ent
```

**Result:** Shows Monthly/Annual subscriptions + both onboarding options

---

### Full Setup (Everything)
```bash
STRIPE_PRICE_ID=price_xxxMonthlyPro
ANNUAL_PAYMENT_LINK=https://buy.stripe.com/annual
SETUP_PRO_PAYMENT_LINK=https://buy.stripe.com/setup_pro
SETUP_ENT_PAYMENT_LINK=https://buy.stripe.com/setup_ent
PACK60_PAYMENT_LINK=https://buy.stripe.com/pack60
PACK300_PAYMENT_LINK=https://buy.stripe.com/pack300
PACK1000_PAYMENT_LINK=https://buy.stripe.com/pack1000
SUPPORT_EMAIL=billing@yourdomain.com
```

**Result:** Shows all sections with professional formatting

---

## User Journey Examples

### Journey 1: Solopreneur Starting Out
1. Signs up (free tier, 3 generations)
2. Uses all 3 free generations
3. Sees upgrade section in sidebar
4. Clicks **€29/mo →** button
5. Completes Stripe Checkout
6. Returns to app → subscription activated → unlimited generations

### Journey 2: Agency Needing Setup Help
1. Signs up and tests the product
2. Decides to go Pro + get professional help
3. Clicks **€29/mo →** for subscription
4. Also clicks **Setup — Enterprise €997 →**
5. Books time slot via email after purchase
6. Gets 2 hours of guided integration support

### Journey 3: Heavy User
1. Already has Pro subscription (€29/mo)
2. Sees "Additional Minutes Packs" section
3. Reviews pricing vs usage
4. Clicks **Voice Minutes Pack 300 min [€39 →]**
5. Purchases for billing/accounting purposes
6. (Manual account crediting by support team - automated in future)

---

## FAQ Section Content (Expandable)

When users click the "💡 Payment Options FAQ", they see:

```markdown
What's included in subscriptions?
- Monthly Pro (€29/mo): Unlimited generations, priority processing, commercial license
- Annual Pro (€290/yr): Same as Monthly, but 17% cheaper (2 months free)

What are Setup services?
- One-time onboarding sessions (not recurring). Video call with our team to help you 
  integrate VocalBrand into your workflow.
- Professional (€497): 60 min session, best for solo entrepreneurs and small teams
- Enterprise (€997): 120 min session, best for agencies and larger teams

What are Minutes Packs?
- Additional TTS minutes for billing/accounting purposes.
- These purchases track usage but don't automatically change in-app quotas while 
  features are locked.
- For account crediting or custom enterprise pricing, contact support@yourdomain.com

How do I switch between Monthly and Annual?
- Cancel your Monthly subscription in Stripe, then purchase Annual via the 
  Payment Link above.
- Or contact support@yourdomain.com for assistance with the switch.
```

---

## Mobile Responsive Design

On mobile devices:
- Sidebar collapses to hamburger menu
- Payment options stack vertically
- Buttons remain full-width for easy tapping
- All links work as expected
- FAQ expander still functions

---

## Business Benefits

### For You (SaaS Owner)
✅ **Flexible pricing** without code changes
✅ **Capture different customer segments** (monthly, annual, enterprise)
✅ **Professional services revenue** (high-margin onboarding)
✅ **Usage-based upsells** (minutes packs)
✅ **Test different pricing** by just changing URLs

### For Your Customers
✅ **Clear options** - see all choices in one place
✅ **Annual savings** - 17% discount clearly shown
✅ **Premium support** - enterprise setup available
✅ **Flexible payments** - one-time or recurring
✅ **Professional presentation** - builds trust

---

## Tips for Maximizing Revenue

1. **Start with Monthly + Annual + Setup Pro**
   - These are the easiest to sell
   - Annual gives better cash flow
   - Setup Pro helps with onboarding complex users

2. **Add Minutes Packs later**
   - Only after confirming your ElevenLabs cost structure
   - Use the profitability formula in PRICING.md
   - Price them so you maintain 60-70% margins

3. **Experiment with pricing**
   - Test different Annual prices (€290 vs €249 vs €349)
   - Try bundling Setup with Annual for power users
   - A/B test by changing the Payment Link URLs

4. **Use Setup services strategically**
   - Upsell during onboarding calls
   - Offer as "VIP fast-track" option
   - Bundle with enterprise deals
   - Great for complex use cases (agencies, studios)

---

## Compliance & Safety

✅ **No code changes** - only environment variables
✅ **Respects CONTEXT06** - visual-only improvements
✅ **Backward compatible** - works without Payment Links configured
✅ **Safe deployment** - no breaking changes
✅ **Database isolated** - Payment Links don't modify app state

---

## Next Steps

1. **Create Payment Links in Stripe Dashboard**
   - Follow step-by-step guide in PRICING.md
   - Start with test mode

2. **Add URLs to environment**
   - Locally: `.env` file
   - Cloud: Streamlit Cloud secrets

3. **Test in browser**
   - Verify all links open correctly
   - Check mobile responsive design
   - Test with different configurations

4. **Monitor conversions**
   - Track which options customers choose
   - Adjust pricing based on data
   - Consider adding more options if needed

5. **Go live**
   - Switch to production Stripe keys
   - Update URLs to live Payment Links
   - Announce new pricing options to users
