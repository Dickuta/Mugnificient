import os
import stripe
from typing import Optional
from datetime import datetime
from decimal import Decimal

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")


class PaymentConfig:
    """Payment configuration"""

    def __init__(self):
        self.stripe_enabled = bool(os.getenv("STRIPE_SECRET_KEY"))
        self.stripe_publishable_key = os.getenv(
            "STRIPE_PUBLISHABLE_KEY", "pk_test_placeholder"
        )

    def is_enabled(self) -> bool:
        return self.stripe_enabled


payment_config = PaymentConfig()


def create_payment_intent(
    amount: float, currency: str = "usd", metadata: dict = None
) -> dict:
    """
    Create a Stripe payment intent

    Args:
        amount: Amount in dollars (will be converted to cents)
        currency: Currency code
        metadata: Additional metadata

    Returns:
        Payment intent dict with client_secret
    """
    if not payment_config.stripe_enabled:
        # Return mock payment intent for testing
        return {
            "id": f"pi_mock_{datetime.utcnow().timestamp()}",
            "client_secret": f"pi_mock_{datetime.utcnow().timestamp()}_secret",
            "amount": int(amount * 100),
            "currency": currency,
            "status": "requires_payment_method",
            "mock": True,
        }

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe uses cents
            currency=currency,
            metadata=metadata or {},
            automatic_payment_methods={"enabled": True},
        )
        return {
            "id": intent.id,
            "client_secret": intent.client_secret,
            "amount": intent.amount,
            "currency": intent.currency,
            "status": intent.status,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Payment failed: {str(e)}")


def confirm_payment(payment_intent_id: str) -> dict:
    """Confirm a payment"""
    if not payment_config.stripe_enabled or payment_intent_id.startswith("pi_mock"):
        return {"id": payment_intent_id, "status": "succeeded", "mock": True}

    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {
            "id": intent.id,
            "status": intent.status,
            "amount": intent.amount,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to confirm payment: {str(e)}")


def refund_payment(payment_intent_id: str, amount: Optional[float] = None) -> dict:
    """Refund a payment"""
    if not payment_config.stripe_enabled or payment_intent_id.startswith("pi_mock"):
        return {"id": payment_intent_id, "status": "refunded", "mock": True}

    try:
        refund_params = {"payment_intent": payment_intent_id}
        if amount:
            refund_params["amount"] = int(amount * 100)

        refund = stripe.Refund.create(**refund_params)
        return {
            "id": refund.id,
            "status": refund.status,
            "amount": refund.amount,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Refund failed: {str(e)}")


def create_checkout_session(
    success_url: str,
    cancel_url: str,
    line_items: list,
    customer_email: Optional[str] = None,
    metadata: dict = None,
) -> dict:
    """Create a Stripe checkout session"""
    if not payment_config.stripe_enabled:
        # Return mock session
        return {
            "id": f"cs_mock_{datetime.utcnow().timestamp()}",
            "url": f"{cancel_url}?mock=true",
            "mock": True,
        }

    try:
        session_params = {
            "payment_method_types": ["card"],
            "line_items": line_items,
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": metadata or {},
        }

        if customer_email:
            session_params["customer_email"] = customer_email

        session = stripe.checkout.Session.create(**session_params)
        return {
            "id": session.id,
            "url": session.url,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Checkout session failed: {str(e)}")
