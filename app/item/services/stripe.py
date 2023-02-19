import logging
from typing import Any, Dict

import stripe
from django.conf import settings

logger = logging.getLogger(__name__)


class StripePayment:
    def create_checkout_session(self, price_data: Dict) -> Any:
        try:
            success_url = self.request.META.get("HTTP_REFERER") + "?session_id={CHECKOUT_SESSION_ID}"
            checkout_session = stripe.checkout.Session.create(
                api_key=settings.STRIPE_SECRET,
                line_items=[price_data],
                mode="payment",
                success_url=success_url,
                cancel_url=self.request.META.get("HTTP_REFERER"),
            )
        except Exception as err:
            logger.error("Create checkout session error: %s", err)
            return None

        logger.debug("Checkout session created: %s", checkout_session)
        return checkout_session

    @staticmethod
    def stripe_price(name: str, amount: int, description: str = None, currency: str = "usd") -> Dict:
        """Prepares Stripe formatted price data
        """
        price_data = {
            "quantity": 1,
            "price_data": {
                "currency": currency,
                "unit_amount": amount,
                "product_data": {
                    "name": name,
                    "description": description or "No description",
                },
            },
        }
        return price_data
