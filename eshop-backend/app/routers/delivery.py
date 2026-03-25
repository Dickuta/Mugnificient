from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.delivery import (
    create_delivery,
    track_delivery,
    cancel_delivery,
    DeliveryStatus,
)
from app.models.models import User, Order

router = APIRouter(prefix="/delivery", tags=["delivery"])


class CreateDeliveryRequest(BaseModel):
    order_id: int
    provider: Optional[str] = None


@router.post("/create")
def create_delivery_shipment(
    request: CreateDeliveryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a delivery shipment for an order"""
    # Get order
    order = db.query(Order).filter(Order.id == request.order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check permissions
    if not current_user.is_staff and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not order.is_paid:
        raise HTTPException(status_code=400, detail="Order must be paid first")

    # Prepare recipient info
    recipient = {
        "name": order.shipping_name,
        "address": f"{order.shipping_address_line1}, {order.shipping_address_line2}",
        "city": order.shipping_city,
        "state": order.shipping_state,
        "zip": order.shipping_zip_code,
        "country": order.shipping_country,
        "phone": order.shipping_phone,
    }

    # Prepare items
    items = []
    for item in order.items:
        items.append(
            {
                "name": item.product_name,
                "quantity": item.quantity,
                "price": float(item.product_price),
            }
        )

    # Create delivery
    try:
        shipment = create_delivery(
            order_id=order.id,
            recipient=recipient,
            items=items,
            provider=request.provider,
        )

        # Update order with tracking info
        order.tracking_number = shipment.get("tracking_number")
        order.delivery_provider = shipment.get("provider", "inhouse")
        order.status = "shipped"
        order.shipped_at = datetime.utcnow()

        # Add estimated delivery to response
        shipment["estimated_delivery"] = shipment.get("estimated_delivery")

        db.commit()

        return shipment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/track/{tracking_number}")
def track_shipment(
    tracking_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Track a delivery shipment"""
    # Find order by tracking number
    order = db.query(Order).filter(Order.tracking_number == tracking_number).first()

    if not order:
        # Try without order lookup
        pass

    try:
        tracking_info = track_delivery(
            tracking_number, order.delivery_provider if order else None
        )
        return tracking_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cancel/{tracking_number}")
def cancel_shipment(
    tracking_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a delivery shipment"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    order = db.query(Order).filter(Order.tracking_number == tracking_number).first()

    if order and order.delivery_provider:
        provider = order.delivery_provider
    else:
        provider = None

    try:
        result = cancel_delivery(tracking_number, provider)

        if result.get("status") == "cancelled" and order:
            order.status = "cancelled"
            db.commit()

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/providers")
def list_providers():
    """List available delivery providers"""
    return {
        "providers": [
            {
                "id": "inhouse",
                "name": "InHouse Delivery",
                "description": "Our own delivery service",
            },
            {"id": "dhl", "name": "DHL", "description": "International shipping"},
        ],
        "default": "inhouse",
    }
