"""FastAPI webhook server for Stripe events.
Run separately: uvicorn vocalbrand.webhook_server:app --reload --port 8787
"""
from __future__ import annotations
import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from auth import set_subscription, get_user, _get_conn

app = FastAPI(title="VocalBrand Webhooks")

stripe.api_key = os.getenv("STRIPE_API_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

@app.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None
    if WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, WEBHOOK_SECRET
            )
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    else:
        # Unsigned fallback (dev only)
        try:
            event = stripe.Event.construct_from(await request.json(), stripe.api_key)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    etype = event["type"]
    data = event["data"]["object"]

    if etype == "checkout.session.completed":
        client_ref = data.get("client_reference_id")
        sub_id = data.get("subscription")
        if client_ref and client_ref.startswith("user_"):
            uid = client_ref.replace("user_", "")
            try:
                uid_int = int(uid)
                set_subscription(uid_int, True, stripe_sub_id=sub_id)
            except ValueError:
                pass
    elif etype in ("customer.subscription.deleted", "customer.subscription.canceled"):
        sub_id = data.get("id")
        # naive: set all users with that sub id to inactive
        conn = _get_conn()
        cur = conn.execute("SELECT id FROM users WHERE stripe_subscription_id=?", (sub_id,))
        rows = cur.fetchall()
        for r in rows:
            set_subscription(r[0], False)
        conn.close()

    return JSONResponse({"received": True})

@app.get("/health")
async def health():
    return {"status": "ok"}
