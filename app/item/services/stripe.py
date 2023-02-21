import logging
from typing import Any, Dict

import stripe
from django.conf import settings
from django.views.generic import View

logger = logging.getLogger(__name__)


class StripePaymentMixin(View):
    api_secret = settings.STRIPE_SECRET
    currency = settings.STRIPE_CURRENCY
    session_arg = "session_id"

    def create_checkout_session(self, price_data: Dict) -> Any:
        try:
            full_path = self.request.META.get("HTTP_REFERER").split("?")[0]
            success_url = "{0}?{1}={2}".format(
                full_path,
                self.session_arg,
                "{CHECKOUT_SESSION_ID}"
            )
            checkout_session = stripe.checkout.Session.create(
                api_key=self.api_secret,
                line_items=[price_data],
                mode="payment",
                success_url=success_url,
                cancel_url=full_path,
            )
        except Exception as err:
            logger.error("Create checkout session error: %s", err)
            return None

        logger.debug("Checkout session created: %s", checkout_session)
        return checkout_session

    def get_payment_session(self):
        payment_session = self.request.GET.get(self.session_arg)
        if payment_session:
            session = stripe.checkout.Session.retrieve(
                payment_session,
                self.api_secret
            )
            logger.debug("Payment session %s", session)

            return session

    def stripe_price(self, name: str, amount: int, description: str = None) -> Dict:
        """Prepares Stripe formatted price data
        """
        price_data = {
            "quantity": 1,
            "price_data": {
                "currency": self.currency,
                "unit_amount": amount,
                "product_data": {
                    "name": name,
                    "description": description or "No description",
                },
            },
        }
        return price_data
