# VocalBrand MVP (Streamlit)

Ultra-fast voice cloning SaaS prototype built for rapid launch: upload voice sample -> clone -> generate speech -> upgrade.

## 🆕 Recent Updates

**Critical Fix (Usage Tracking):** Free-tier usage limit now persists across sessions and refreshes via database storage. See [CRITICAL_FIX_USAGE_TRACKING.md](./CRITICAL_FIX_USAGE_TRACKING.md) for testing instructions.

**Enhanced Payment Options:** Flexible pricing with Annual subscriptions, Professional onboarding services, and Minutes Packs—all configurable via Payment Links. See [PAYMENT_OPTIONS_VISUAL_GUIDE.md](./PAYMENT_OPTIONS_VISUAL_GUIDE.md) for UI preview.

## Documentation Quick Links

- **[PRICING.md](./PRICING.md)** - Complete Stripe setup guide, pricing formulas, cost model
- **[PAYMENT_OPTIONS_VISUAL_GUIDE.md](./PAYMENT_OPTIONS_VISUAL_GUIDE.md)** - How payment options appear in UI
- **[CRITICAL_FIX_USAGE_TRACKING.md](./CRITICAL_FIX_USAGE_TRACKING.md)** - Testing the persistent usage counter
- **[SECRETS_REFERENCE.md](./SECRETS_REFERENCE.md)** - All environment variables explained

---

## Payment & Pricing

> Full guide: [PRICING.md](./PRICING.md)

### Subscription Plans (no code changes)
- **Monthly Pro** (€29/mo) - Managed via `STRIPE_PRICE_ID` (in-app checkout button)
- **Annual Pro** (€290/yr) - Optional Payment Link via `ANNUAL_PAYMENT_LINK` (17% savings)

### One-time Services (Payment Links - optional)
Configure these environment variables to show professional onboarding options in the upgrade section:

```bash
SETUP_PRO_PAYMENT_LINK=https://buy.stripe.com/...    # Professional (€497, 60 min)
SETUP_ENT_PAYMENT_LINK=https://buy.stripe.com/...    # Enterprise (€997, 120 min)
```

### Additional Minutes Packs (Payment Links - optional)
```bash
PACK60_PAYMENT_LINK=https://buy.stripe.com/...       # 60 min pack
PACK300_PAYMENT_LINK=https://buy.stripe.com/...      # 300 min pack
PACK1000_PAYMENT_LINK=https://buy.stripe.com/...     # 1000 min pack
```

**Notes:**
- Payment Links are visual shortcuts only. Purchases don't automatically change in-app state while features are locked.
- The in-app subscription button continues to use `STRIPE_PRICE_ID` via Stripe Checkout (unaffected).
- Only configure the links you actually created in Stripe. The UI adapts automatically.

## Authentication Gate
- Voice cloning and speech generation now require a signed-in user. Guests can browse the landing copy but must log in or register before recording/uploading audio or hitting the ElevenLabs APIs. Session state is reset on logout to prevent lingering access.

## New Modules
- `auth.py` (SQLite user accounts)
- `webhook_server.py` (FastAPI Stripe webhook receiver)
- `db_init.py` (initialize DB + demo user)
- `SECRETS_REFERENCE.md` (detailed secrets documentation)

## Auth Flow (MVP)
1. User registers with email + password (stored hashed via bcrypt)
2. User logs in – session stores `user_id`
3. Generations tracked per session (can move to DB later)
4. Upgrade triggers Stripe Checkout; webhook marks subscription active

## Running Webhook Server (Local Dev)
1. Start FastAPI server:
```
uvicorn vocalbrand.webhook_server:app --port 8787 --reload
```
2. In another terminal run Stripe CLI to forward events:
```
stripe listen --forward-to localhost:8787/stripe
```
3. Add the printed signing secret to `STRIPE_WEBHOOK_SECRET`.
4. Complete a test Checkout → webhook sets `subscription_active=1` for user.

## Secrets Summary
See `SECRETS_REFERENCE.md` for full annotated examples.
Minimum for production-like run:
```
ELEVENLABS_API_KEY
STRIPE_API_KEY
STRIPE_PRICE_ID
STRIPE_WEBHOOK_SECRET
APP_SECRET_KEY
DATABASE_URL
```
Offline demo:
```
VOCALBRAND_OFFLINE=1
APP_SECRET_KEY=dev_key
DATABASE_URL=sqlite:///vocalbrand.db
```

## Database
SQLite file path from `DATABASE_URL` (default `vocalbrand.db`). Use `db_init.py` to initialize.

## Hashing Scheme
By default passwords use bcrypt. If you hit Windows-specific bcrypt backend issues, switch to PBKDF2:
```
set AUTH_HASH_SCHEME=pbkdf2   # Windows PowerShell: $env:AUTH_HASH_SCHEME="pbkdf2"
```
Supported: `bcrypt` | `pbkdf2` (pbkdf2_sha256). Long passwords are truncated to 72 bytes for bcrypt compatibility.

## Audio Recorder Dependencies
- The optional in-browser recorder depends on FFmpeg. Install FFmpeg locally and ensure `ffmpeg`/`ffprobe` are on the system `PATH`, or point the app to explicit binaries via `FFMPEG_BINARY` and `FFPROBE_BINARY` environment variables.
- When FFmpeg is unavailable, the Streamlit app falls back to pure file uploads and displays a diagnostic banner instead of crashing.

## Roadmap Additions
- JWT / secure session tokens
- Email verification & password resets
- Voice asset persistence + listing
- Usage quotas enforced server-side
- Metrics panel & Sentry dashboards
- Blue/Green: two deployed Streamlit apps + traffic cutover

## Environment Organization (Single Source of Truth)
Active virtual environment directory (keep ONLY this one in repo root):
```
vocalbrand_supreme/   # (OPTIONAL rename locally to vocalbrand_supreme_venv for clarity)
```
DO NOT create parallel `.venv` or `venv` folders—consistency prevents “which interpreter?” errors.

Activate on Windows PowerShell:
```
cd <project_root>
vocalbrand_supreme\Scripts\Activate.ps1
```
Install/update deps:
```
pip install -r requirements.txt
```
If you prefer a clearer name you can rename the folder to `vocalbrand_supreme_venv` (update your activation path accordingly). Avoid committing multiple venvs; `.gitignore` already excludes them.

To recreate cleanly (e.g., after corruption):
```
Remove-Item -Recurse -Force vocalbrand_supreme
python -m venv vocalbrand_supreme
vocalbrand_supreme\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```
Then run:
```
streamlit run app.py
```

## Recorder / FFmpeg Behavior in Deployment
| Scenario | Behavior |
|----------|----------|
| FFmpeg present on PATH | Recorder component enabled automatically |
| AUTO_FFMPEG=1 & no FFmpeg | App attempts lightweight download to `./ffmpeg/bin` (Windows) |
| Missing & AUTO_FFMPEG not set | Upload fallback; warning shown |
| HIDE_RECORDER_IF_NO_FFMPEG=1 | Warning suppressed; only upload UI rendered |

Environment flags:
```
AUTO_FFMPEG=1               # try auto bootstrap (static essentials build)
FFMPEG_DIR=C:\ffmpeg        # explicit root (bin must contain ffmpeg.exe)
HIDE_RECORDER_IF_NO_FFMPEG=1 # hide warning banner in production
```

If deploying to Streamlit Cloud and recorder is important, bake FFmpeg via a custom build image or rely on upload fallback until a backend capture alternative is added.

## Features & Behavior (Locked)
The app’s behavior and feature set are now LOCKED (see `CONTEXT06_MANDATORY.txt`). Any change must preserve the following:

- Recording options
	- Native components when available: `streamlit-audiorecorder` or `streamlit_audio_recorder`
	- Cloud-friendly fallback: `streamlit_mic_recorder` (auto-installed at runtime if missing, also pinned in requirements)
	- Pro Recorder (HTML5, timer + waveform) with base64 ingest and upload link
	- Upload fallback (WAV/MP3/M4A)
- FFmpeg handling
	- Cross‑platform detection (Windows .exe, Linux no‑ext)
	- Streamlit Cloud installs: `packages.txt` includes `ffmpeg`, `libavcodec-extra`, `libsndfile1`, `portaudio19-dev`
	- Local Windows: existing FFmpeg respected; no behavior change
- Core flows
	- Authentication (login/register), subscription & Stripe Checkout, webhook server, offline mode option
	- Voice cloning and speech generation remain unchanged
	- Metrics and DB behavior preserved
- UX improvements (non-breaking)
	- Mobile-first navigation reliability: sticky hamburger, larger tap targets, overlay z-index fix
	- Elegant step dots for phases (`utils/ui.py: render_steps`) without changing flow logic
	- Visual polish via CSS only; labels and step order unchanged

Deploy notes (Cloud):
- `requirements.txt` includes recorder components and `streamlit-mic-recorder`
- `packages.txt` ensures system libraries for audio are present
- No large binaries are committed
