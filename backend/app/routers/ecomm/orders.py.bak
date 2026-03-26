from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
import random
import string
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.core.emails import send_order_confirmation, send_order_shipped
from app.core.websocket import manager
from app.core.forecasting import ForecastingService
from app.core.inventory_ml import get_inventory_ml
from app.models.models import Order, OrderItem, Cart, CartItem, Product, User
from app.schemas.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])


def generate_order_number():
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{date_str}-{random_str}"


@router.get("/", response_model=List[OrderResponse])
def list_orders(user_id: int, db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return orders


@router.get("/{order_number}", response_model=OrderResponse)
def get_order(order_number: str, user_id: int, db: Session = Depends(get_db)):
    order = (
        db.query(Order)
        .filter(Order.order_number == order_number, Order.user_id == user_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/checkout", response_model=OrderResponse)
def checkout(order: OrderCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == order.user_id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Get user for email
    user = db.query(User).filter(User.id == order.user_id).first()

    subtotal = Decimal(0)
    order_items_data = []

    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            subtotal += product.price * item.quantity
            order_items_data.append(
                {
                    "name": product.name,
                    "quantity": item.quantity,
                    "price": float(product.price),
                }
            )

    shipping_cost = Decimal(10.00)
    tax = subtotal * Decimal(0.08)
    total = subtotal + shipping_cost + tax

    order_number = generate_order_number()

    db_order = Order(
        user_id=order.user_id,
        order_number=order_number,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax=tax,
        total=total,
        shipping_name=order.shipping_name,
        shipping_address_line1=order.shipping_address_line1,
        shipping_address_line2=order.shipping_address_line2,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_zip_code=order.shipping_zip_code,
        shipping_country=order.shipping_country,
        shipping_phone=order.shipping_phone,
        notes=order.notes,
    )
    db.add(db_order)
    db.flush()

    forecasting = ForecastingService(db)
    
    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            order_item = OrderItem(
                order_id=db_order.id,
                product_id=product.id,
                product_name=product.name,
                product_price=product.price,
                quantity=item.quantity,
                subtotal=product.price * item.quantity,
            )
            db.add(order_item)
            product.stock -= item.quantity
            
            revenue = float(product.price * item.quantity)
            forecasting.record_sales(
                product_id=product.id,
                date=datetime.utcnow(),
                quantity=item.quantity,
                revenue=revenue
            )
            
            db.flush()

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(db_order)

    # Send order confirmation email
    if user and user.email:
        send_order_confirmation(
            to_email=user.email,
            order_number=order_number,
            total=float(total),
            items=order_items_data,
            customer_name=user.first_name or user.username,
        )

    # Send WebSocket notification
    if user:
        background_tasks.add_task(
            manager.send_order_update,
            user.id,
            {
                "order_number": order_number,
                "total": float(total),
                "status": "confirmed",
            },
        )

    # Trigger inventory ML stock deduction and auto refill
    try:
        ml = get_inventory_ml(db)
        ml.deduct_stock_on_purchase(db_order.id)
    except Exception as e:
        logger.error(f"Failed to update inventory: {e}")

    return db_order


@router.post("/{order_number}/pay")
def mark_order_paid(order_number: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.is_paid = True
    order.paid_at = datetime.utcnow()
    order.status = "processing"
    db.commit()

    # Send shipped notification
    user = db.query(User).filter(User.id == order.user_id).first()
    if user and user.email:
        send_order_shipped(
            to_email=user.email,
            order_number=order_number,
            customer_name=user.first_name or user.username,
        )

    return {"message": "Order marked as paid"}


# Import asyncio for async operations
import asyncio
