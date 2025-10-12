"""Stripe payment management with graceful fallbacks.

Enhancements:
- Dynamic success/cancel URLs pointing back to the running app
- Basic verification helper to retrieve Checkout Session and Subscription ID
"""
from __future__ import annotations
import os
from typing import Optional, Tuple
import urllib.parse
import stripe


class PaymentManager:
    def __init__(self, api_key: str, price_id: Optional[str] = None, price_id_annual: Optional[str] = None, return_url_base: Optional[str] = None):
        stripe.api_key = api_key
        self.price_id = price_id  # Monthly price ID
        self.price_id_annual = price_id_annual  # Annual price ID
        self.monthly_amount_cents = 4900
        # Base URL to send users back to the app (e.g., http://localhost:8501 or https://yourdomain)
        self.return_url_base = return_url_base or os.getenv("APP_BASE_URL", "http://localhost:8501")
        # Optional hard overrides shared across apps
        self.success_url_override = os.getenv("STRIPE_SUCCESS_URL")
        self.cancel_url_override = os.getenv("STRIPE_CANCEL_URL")

    def _success_url(self) -> str:
        # Prefer global override; append session_id and optional return_to back to app
        if self.success_url_override:
            base = self.success_url_override.rstrip("?")
            return_to = urllib.parse.quote(self.return_url_base, safe="")
            sep = "&" if "?" in base else "?"
            return f"{base}{sep}session_id={{CHECKOUT_SESSION_ID}}&return_to={return_to}"
        # Default:
        return f"{self.return_url_base}/?billing=success&session_id={{CHECKOUT_SESSION_ID}}"

    def _cancel_url(self) -> str:
        if self.cancel_url_override:
            base = self.cancel_url_override.rstrip("?")
            return_to = urllib.parse.quote(self.return_url_base, safe="")
            sep = "&" if "?" in base else "?"
            return f"{base}{sep}return_to={return_to}"
        return f"{self.return_url_base}/?billing=cancel"

    def create_checkout_session(self, user_ref: str, plan: str = "monthly", price_id: Optional[str] = None, mode: str = "subscription") -> Tuple[str, Optional[str]]:
        """Create a Stripe Checkout session for subscription or one-time payment.
        
        Args:
            user_ref: User reference ID (e.g., "user_123")
            plan: "monthly" or "annual" (default: "monthly") - used for subscription mode
            price_id: Optional explicit Price ID to use (for one-time payments or overrides)
            mode: "subscription" or "payment" (default: "subscription")
        
        Returns:
            Tuple of (checkout_url, session_id)
        """
        try:
            # Select price ID
            if price_id:
                price_to_use = price_id
            elif plan == "annual" and self.price_id_annual:
                price_to_use = self.price_id_annual
            else:
                price_to_use = self.price_id
            
            kwargs = {
                "mode": mode,
                "success_url": self._success_url(),
                "cancel_url": self._cancel_url(),
                "client_reference_id": user_ref,
                "metadata": {"user_ref": user_ref, "plan": plan},
            }
            if price_to_use:
                kwargs["line_items"] = [{"price": price_to_use, "quantity": 1}]
            else:
                # Fallback to creating price on the fly (monthly subscription only)
                kwargs["line_items"] = [
                    {
                        "price_data": {
                            "currency": "usd",
                            "recurring": {"interval": "month"},
                            "unit_amount": self.monthly_amount_cents,
                            "product_data": {"name": "VocalBrand Pro Monthly"},
                        },
                        "quantity": 1,
                    }
                ]
            session = stripe.checkout.Session.create(**kwargs)
            return session.url, session.id
        except Exception:
            # Fallback hosted link in worst case
            return f"https://buy.stripe.com/test_fallback_{user_ref}", None

    def get_checkout_session(self, session_id: str):
        try:
            # Expand line items for one-time payments; in subscription mode, subscription field is present
            return stripe.checkout.Session.retrieve(
                session_id,
                expand=["line_items", "line_items.data.price", "payment_intent", "customer"]
            )
        except Exception:
            return None

    def get_subscription_id_from_session(self, session_id: str) -> Optional[str]:
        sess = self.get_checkout_session(session_id)
        if not sess:
            return None
        # On completed, Stripe includes subscription field
        sub_id = sess.get("subscription") if isinstance(sess, dict) else getattr(sess, "subscription", None)
        return sub_id

    def get_line_items_summary(self, session_id: str):
        """Return a lightweight summary of line items for a checkout session.

        Output shape: {
            "mode": "payment"|"subscription",
            "items": [
                {"price_id": str|None, "product": str|None, "quantity": int, "amount_cents": int|None, "currency": str|None}
            ],
            "customer_email": str|None,
            "amount_total": int|None,
            "currency": str|None,
        }
        """
        sess = self.get_checkout_session(session_id)
        if not sess:
            return None
        # Normalize access whether dict or StripeObject
        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        mode = g(sess, "mode")
        email = None
        cust = g(sess, "customer_details") or g(sess, "customer")
        if isinstance(cust, dict):
            email = cust.get("email")
        else:
            # customer may be an ID when not expanded; try nested customer_details
            cdet = g(sess, "customer_details")
            if isinstance(cdet, dict):
                email = cdet.get("email")
        amount_total = g(sess, "amount_total")
        currency = g(sess, "currency")

        items = []
        li = g(sess, "line_items")
        data = g(li, "data") if isinstance(li, (dict, object)) else None
        if data and isinstance(data, list):
            for it in data:
                price = g(it, "price")
                price_id = None
                amount_cents = None
                curr = None
                product_name = None
                if isinstance(price, dict):
                    price_id = price.get("id")
                    amount_cents = price.get("unit_amount") or price.get("unit_amount_decimal")
                    curr = price.get("currency")
                    prod = price.get("product")
                    if isinstance(prod, dict):
                        product_name = prod.get("name")
                qty = g(it, "quantity", 1) or 1
                items.append({
                    "price_id": price_id,
                    "product": product_name,
                    "quantity": int(qty),
                    "amount_cents": amount_cents if amount_cents is None else int(amount_cents),
                    "currency": curr or currency,
                })
        return {
            "mode": mode,
            "items": items,
            "customer_email": email,
            "amount_total": amount_total,
            "currency": currency,
        }

    def is_subscription_active(self, user_ref: str) -> bool:
        # Placeholder: caller should rely on DB or webhook; keep signature for compatibility
        return False
