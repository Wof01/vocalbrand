# VocalBrand Secrets & Environment Reference

Two supported secret loading strategies:
1. `vocalbrand/.streamlit/secrets.toml` (Streamlit native)
2. `.env` file (loaded by dotenv if you add explicit loading code) — not yet auto-loaded; you can add `from dotenv import load_dotenv; load_dotenv()` early in `app.py` if desired.

Below are canonical templates.

## secrets.toml (Place in `vocalbrand/.streamlit/secrets.toml`)
```toml
# ================= CORE EXTERNAL SERVICE KEYS =================
# ElevenLabs API key (required for real cloning). Leave blank + set VOCALBRAND_OFFLINE=1 for offline simulation.
ELEVENLABS_API_KEY = "pk_elevenlabs_xxxxxxxxxxxxxxxxx"

# Stripe secret API key (required for creating Checkout Sessions). Use test key first: sk_test_...
STRIPE_API_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxx"

# Stripe price ID for the recurring $49 subscription (pre-created in Stripe dashboard) e.g. price_12345
STRIPE_PRICE_ID = "price_XXXXXXXXXXXXXXXX"

# Stripe webhook signing secret (from Stripe CLI or dashboard) used by webhook_server.py to verify events
STRIPE_WEBHOOK_SECRET = "whsec_XXXXXXXXXXXXXXXXXXXXXXXX"

# Sentry DSN for error monitoring (optional). Leave blank to disable.
SENTRY_DSN = "https://public@sentry.io/projectid"

# AWS S3 or other storage credentials (OPTIONAL - future use)
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_S3_BUCKET = ""

# ================= AUTH / SECURITY =================
# Secret key for signing session tokens / password reset tokens. CHANGE IN PRODUCTION.
APP_SECRET_KEY = "change_this_super_secret_key"

# Pepper added to password hashing (optional extra defense). Keep private.
PASSWORD_PEPPER = "optional_pepper_string"

# ================= DATABASE / STORAGE =================
# SQLite filename (local dev). For cloud migration switch to Postgres and update DSN.
DATABASE_URL = "sqlite:///vocalbrand.db"

# ================= FEATURE FLAGS =================
# Set to 1 to force offline mode (no external API calls) for demos.
VOCALBRAND_OFFLINE = "0"

# Enable verbose debug logging (1=on, 0=off).
DEBUG_LOGGING = "0"

# ================= ANALYTICS / OPTIONAL =================
# Future integration placeholders (Mixpanel, Segment, etc.)
MIXPANEL_TOKEN = ""
SEGMENT_WRITE_KEY = ""

# ================= EMAIL (OPTIONAL) =================
# SMTP credentials if you want to send verification / reset emails.
SMTP_HOST = ""
SMTP_PORT = "587"
SMTP_USERNAME = ""
SMTP_PASSWORD = ""
SMTP_FROM_EMAIL = "no-reply@vocalbrand.com"
```

## .env (Optional Alternative)
If you prefer environment variables instead of secrets.toml:
```env
ELEVENLABS_API_KEY=pk_elevenlabs_xxxxxxxxxxxxxxxxx
STRIPE_API_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_PRICE_ID=price_XXXXXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXX
SENTRY_DSN=https://public@sentry.io/projectid
APP_SECRET_KEY=change_this_super_secret_key
PASSWORD_PEPPER=optional_pepper_string
DATABASE_URL=sqlite:///vocalbrand.db
VOCALBRAND_OFFLINE=0
DEBUG_LOGGING=0
MIXPANEL_TOKEN=
SEGMENT_WRITE_KEY=
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=no-reply@vocalbrand.com
```

## Minimal Set To Run Full (Production-like)
```
ELEVENLABS_API_KEY
STRIPE_API_KEY
STRIPE_PRICE_ID
STRIPE_WEBHOOK_SECRET
APP_SECRET_KEY
DATABASE_URL
```

## Minimal Set To Run Offline Demo
```
VOCALBRAND_OFFLINE=1
APP_SECRET_KEY=dev_key
DATABASE_URL=sqlite:///vocalbrand.db
```

## Notes
- Never commit real keys. Add `secrets.example.toml` (already present) and keep actual secrets local.
- To use `.env`, add in `app.py` (top):
```python
from dotenv import load_dotenv
load_dotenv()
```
- `APP_SECRET_KEY` will later be used for signing JWT/session tokens.
- `PASSWORD_PEPPER` should be static and not stored alongside hashed passwords.
