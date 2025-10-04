Netlify Billing Pages

This folder contains a tiny static site (success + cancel) you can zip and drag into Netlify to deploy quickly.

Standard URLs after deploy (assuming site base https://YOUR-SITE.netlify.app):
- Success: https://YOUR-SITE.netlify.app/success/
- Cancel:  https://YOUR-SITE.netlify.app/cancel/

Both pages accept the following query parameters appended by Stripe/your app:
- session_id: Stripe Checkout session id (success only)
- return_to: URL-encoded URL of your app (e.g., https://vocalbrand.app or http://localhost:8501)

Behavior:
- Success page shows a friendly confirmation, displays the session id, and provides a manual "Back to app" button which sends users to `return_to?billing=success&session_id=...`.
- Cancel page explains that the checkout was canceled and provides a manual "Back to app" button which sends users to `return_to?billing=cancel`.
   (Auto-redirect is intentionally disabled to avoid browser or host-specific redirect loops.)

How to deploy (manual upload)
1. Open the `netlify_billing` folder, SELECT ALL inner items (success/, cancel/, _redirects, site.css, logo.png, readme.md), then right-click → Send to → Compressed (zipped) folder.
   - Important: Zip the contents, not the parent folder. The zip root must contain `success/`, `cancel/`, `_redirects`, etc. If you zip a parent folder, Netlify will deploy with an extra folder level (e.g., `/vocalbrand/success/`) and your routes will not match.
2. In Netlify → Your site → Deploys: drag-and-drop that zip. After publish, the Deploy file browser must show `success/`, `cancel/`, `_redirects` at the ROOT (no extra folder at the top level).
3. Verify endpoints:
   - https://YOUR-SITE.netlify.app/success/
   - https://YOUR-SITE.netlify.app/cancel/
3. In your app environment, set:
   - STRIPE_SUCCESS_URL = https://YOUR-SITE.netlify.app/success/
   - STRIPE_CANCEL_URL  = https://YOUR-SITE.netlify.app/cancel/
   - APP_BASE_URL       = https://YOUR-APP-DOMAIN (or http://localhost:8501 for dev)

Configure your app
- Set environment variables:
   - `STRIPE_SUCCESS_URL` = `https://YOUR-SITE.netlify.app/success`
   - `STRIPE_CANCEL_URL`  = `https://YOUR-SITE.netlify.app/cancel`
   - `APP_BASE_URL`       = `https://YOUR-APP-DOMAIN` (or `http://localhost:8501` for dev)
   Trailing slash is optional; `_redirects` handles both.

Notes
- You can swap the branding/logo by editing `site.css` and the `<img>` in each page.
- If JavaScript is disabled, the manual buttons still work.
- If you see “too many redirects”, the Netlify page is likely redirecting to itself or the site has a global redirect rule. Make sure `_redirects` is at the site ROOT (not nested), and that `return_to` points back to YOUR APP (not to Netlify). PaymentManager already appends `return_to=APP_BASE_URL`.

Quick manual test (no Stripe):
- Visit: `https://YOUR-SITE.netlify.app/success/?session_id=test123&return_to=http%3A%2F%2Flocalhost%3A8501`
- The page should load once and the "Back to app" button should point to `http://localhost:8501/?billing=success&session_id=test123`.
