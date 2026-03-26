from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.payments import (
    create_payment_intent,
    confirm_payment,
    refund_payment,
    create_checkout_session,
    payment_config,
)
from app.core.delivery import create_delivery, track_delivery, DeliveryStatus
from app.core.retry import with_retry, call_with_circuit_breaker, payment_circuit_breaker, delivery_circuit_breaker
from app.models.models import User, Order, OrderItem

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentRequest(BaseModel):
    amount: float
    order_id: int


class CheckoutRequest(BaseModel):
    order_id: int
    success_url: str
    cancel_url: str


class DeliveryRequest(BaseModel):
    order_id: int
    provider: Optional[str] = None


@router.get("/config")
def get_payment_config():
    """Get payment configuration"""
    return {
        "stripe_enabled": payment_config.stripe_enabled,
        "stripe_publishable_key": payment_config.stripe_publishable_key
        if payment_config.stripe_enabled
        else None,
    }


@router.post("/create-intent")
def create_intent(
    payment: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a payment intent"""
    # Verify order belongs to user
    order = (
        db.query(Order)
        .filter(Order.id == payment.order_id, Order.user_id == current_user.id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.is_paid:
        raise HTTPException(status_code=400, detail="Order already paid")

    try:
        intent = create_payment_intent(
            amount=float(order.total),
            metadata={"order_id": order.id, "user_id": current_user.id},
        )
        return intent
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirm")
def confirm_payment_endpoint(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Confirm a payment"""
    try:
        result = confirm_payment(payment_intent_id)

        if result.get("status") == "succeeded":
            # Find order by payment intent (stored in order)
            # For now, update all unpaid orders for this user
            order = (
                db.query(Order)
                .filter(Order.user_id == current_user.id, Order.is_paid == False)
                .first()
            )

            if order:
                order.is_paid = True
                order.paid_at = datetime.utcnow()
                order.status = "paid"
                db.commit()

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/checkout-session")
def create_checkout(
    checkout: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe checkout session"""
    order = (
        db.query(Order)
        .filter(Order.id == checkout.order_id, Order.user_id == current_user.id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.is_paid:
        raise HTTPException(status_code=400, detail="Order already paid")

    # Create line items for checkout
    line_items = []
    for item in order.items:
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.product_name,
                    },
                    "unit_amount": int(float(item.product_price) * 100),
                },
                "quantity": item.quantity,
            }
        )

    try:
        session = create_checkout_session(
            success_url=checkout.success_url,
            cancel_url=checkout.cancel_url,
            line_items=line_items,
            customer_email=current_user.email,
            metadata={"order_id": order.id},
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refund")
def refund_payment_endpoint(
    payment_intent_id: str,
    amount: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Refund a payment (admin only)"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        result = refund_payment(payment_intent_id, amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
