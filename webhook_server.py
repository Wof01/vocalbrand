"""FastAPI webhook server for Stripe events.
Run separately: uvicorn vocalbrand.webhook_server:app --reload --port 8787

Handles:
- Subscription activations (Monthly/Annual Pro)
- One-time Payment Link purchases (Setup services, Minutes Packs)
- Automatic credit provisioning
"""
from __future__ import annotations
import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from auth import (
    set_subscription,
    get_user,
    get_user_by_email,
    add_minutes_balance,
    add_setup_credits,
    _get_conn,
)

app = FastAPI(title="VocalBrand Webhooks")

stripe.api_key = os.getenv("STRIPE_API_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Product name patterns for automatic detection
MINUTES_PACK_PATTERNS = {
    "60": 60,
    "300": 300,
    "1000": 1000,
    "pack 60": 60,
    "pack 300": 300,
    "pack 1000": 1000,
}

SETUP_PATTERNS = {
    "professional": 1,
    "enterprise": 1,
    "setup": 1,
}


def detect_product_type(product_name: str, amount: int) -> tuple[str, int]:
    """Detect product type from name and amount.
    
    Returns: (type, value) where:
        - type: 'minutes', 'setup', 'subscription', or 'unknown'
        - value: minutes amount or setup credits
    """
    name_lower = product_name.lower()
    
    # Check for minutes packs by name
    for pattern, minutes in MINUTES_PACK_PATTERNS.items():
        if pattern in name_lower:
            return ("minutes", minutes)
    
    # Check for setup services by name
    for pattern, credits in SETUP_PATTERNS.items():
        if pattern in name_lower:
            return ("setup", credits)
    
    # Fallback: detect by amount (your specific prices)
    amount_eur = amount / 100  # Stripe amounts are in cents
    
    if amount_eur == 89:
        return ("minutes", 60)
    elif amount_eur == 399:
        return ("minutes", 300)
    elif amount_eur == 1299:
        return ("minutes", 1000)
    elif amount_eur == 497:
        return ("setup", 1)
    elif amount_eur == 997:
        return ("setup", 1)
    elif amount_eur in (29, 290):
        return ("subscription", 0)
    
    return ("unknown", 0)


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

    # Handle checkout completion (subscriptions AND one-time payments)
    if etype == "checkout.session.completed":
        mode = data.get("mode")  # 'subscription' or 'payment'
        customer_email = data.get("customer_details", {}).get("email")
        client_ref = data.get("client_reference_id")
        sub_id = data.get("subscription")
        amount = data.get("amount_total", 0)
        
        # Get user ID (either from client_reference_id or email lookup)
        uid = None
        if client_ref and client_ref.startswith("user_"):
            try:
                uid = int(client_ref.replace("user_", ""))
            except ValueError:
                pass
        
        if not uid and customer_email:
            user = get_user_by_email(customer_email)
            if user:
                uid = user["id"]
        
        if not uid:
            # Log but don't fail - payment succeeded, we'll handle manually if needed
            print(f"[WARN] Could not identify user for checkout session {data.get('id')}")
            return JSONResponse({"received": True, "warning": "user_not_found"})
        
        # Handle subscription mode
        if mode == "subscription":
            set_subscription(uid, True, stripe_sub_id=sub_id)
            print(f"[INFO] Activated subscription for user {uid}")
        
        # Handle one-time payment mode (Payment Links)
        elif mode == "payment":
            # Fetch line items to get product details
            try:
                session = stripe.checkout.Session.retrieve(
                    data.get("id"),
                    expand=["line_items", "line_items.data.price.product"]
                )
                
                for item in session.line_items.data:
                    product = item.price.product
                    product_name = product.name if hasattr(product, 'name') else str(product)
                    quantity = item.quantity
                    
                    prod_type, value = detect_product_type(product_name, amount)
                    
                    if prod_type == "minutes" and value > 0:
                        total_minutes = value * quantity
                        new_balance = add_minutes_balance(uid, total_minutes)
                        print(f"[INFO] Added {total_minutes} minutes to user {uid}, new balance: {new_balance}")
                    
                    elif prod_type == "setup" and value > 0:
                        total_credits = value * quantity
                        new_credits = add_setup_credits(uid, total_credits)
                        print(f"[INFO] Added {total_credits} setup credits to user {uid}, new total: {new_credits}")
                    
                    elif prod_type == "subscription":
                        # Annual payment link without subscription mode
                        set_subscription(uid, True)
                        print(f"[INFO] Activated subscription via payment link for user {uid}")
                    
                    else:
                        print(f"[WARN] Unknown product type for {product_name}, amount {amount}")
            
            except Exception as e:
                print(f"[ERROR] Failed to process payment link: {e}")
                # Don't fail the webhook - payment succeeded, we'll handle manually if needed
    
    # Handle subscription cancellation
    elif etype in ("customer.subscription.deleted", "customer.subscription.canceled"):
        sub_id = data.get("id")
        conn = _get_conn()
        cur = conn.execute("SELECT id FROM users WHERE stripe_subscription_id=?", (sub_id,))
        rows = cur.fetchall()
        for r in rows:
            set_subscription(r[0], False)
            print(f"[INFO] Deactivated subscription for user {r[0]}")
        conn.close()
    
    # Handle subscription updates (renewal, plan changes)
    elif etype == "customer.subscription.updated":
        sub_id = data.get("id")
        status = data.get("status")
        if status in ("active", "trialing"):
            conn = _get_conn()
            cur = conn.execute("SELECT id FROM users WHERE stripe_subscription_id=?", (sub_id,))
            rows = cur.fetchall()
            for r in rows:
                set_subscription(r[0], True, stripe_sub_id=sub_id)
                print(f"[INFO] Updated subscription status for user {r[0]}")
            conn.close()

    return JSONResponse({"received": True})


@app.get("/health")
async def health():
    return {"status": "ok"}

