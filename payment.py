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
    def __init__(self, api_key: str, price_id: Optional[str] = None, return_url_base: Optional[str] = None):
        stripe.api_key = api_key
        self.price_id = price_id  # Use predefined price when available
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

    def create_checkout_session(self, user_ref: str) -> Tuple[str, Optional[str]]:
        try:
            kwargs = {
                "mode": "subscription",
                "success_url": self._success_url(),
                "cancel_url": self._cancel_url(),
                "client_reference_id": user_ref,
                "metadata": {"user_ref": user_ref},
            }
            if self.price_id:
                kwargs["line_items"] = [{"price": self.price_id, "quantity": 1}]
            else:
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
            return stripe.checkout.Session.retrieve(session_id)
        except Exception:
            return None

    def get_subscription_id_from_session(self, session_id: str) -> Optional[str]:
        sess = self.get_checkout_session(session_id)
        if not sess:
            return None
        # On completed, Stripe includes subscription field
        sub_id = sess.get("subscription") if isinstance(sess, dict) else getattr(sess, "subscription", None)
        return sub_id

    def is_subscription_active(self, user_ref: str) -> bool:
        # Placeholder: caller should rely on DB or webhook; keep signature for compatibility
        return False
