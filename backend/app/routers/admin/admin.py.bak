from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.models.models import User, Product, Category, Order, OrderItem
from app.core.security import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    total_orders = db.query(Order).count()
    total_users = db.query(User).count()

    total_revenue = (
        db.query(func.sum(Order.total)).filter(Order.is_paid == True).scalar() or 0
    )

    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    paid_orders = db.query(Order).filter(Order.is_paid == True).count()

    return {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": float(total_revenue),
        "pending_orders": pending_orders,
        "paid_orders": paid_orders,
    }


@router.get("/sales-by-category")
def get_sales_by_category(
    db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    results = (
        db.query(
            Category.name,
            func.sum(OrderItem.subtotal).label("revenue"),
            func.count(OrderItem.id).label("orders"),
        )
        .join(Product, Product.category_id == Category.id)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.is_paid == True)
        .group_by(Category.name)
        .all()
    )

    return [
        {"category": r[0], "revenue": float(r[1] or 0), "orders": r[2]} for r in results
    ]


@router.get("/sales-over-time")
def get_sales_over_time(
    days: int = 30, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    start_date = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total).label("revenue"),
            func.count(Order.id).label("orders"),
        )
        .filter(Order.created_at >= start_date, Order.is_paid == True)
        .group_by(func.date(Order.created_at))
        .all()
    )

    return [
        {
            "date": r[0].isoformat() if r[0] else None,
            "revenue": float(r[1] or 0),
            "orders": r[2],
        }
        for r in results
    ]


@router.get("/top-products")
def get_top_products(
    limit: int = 10, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    results = (
        db.query(
            Product.name,
            func.sum(OrderItem.quantity).label("quantity_sold"),
            func.sum(OrderItem.subtotal).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.is_paid == True)
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )

    return [
        {"name": r[0], "quantity_sold": r[1] or 0, "revenue": float(r[2] or 0)}
        for r in results
    ]


@router.get("/recent-orders")
def get_recent_orders(
    limit: int = 10, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(limit).all()

    return [
        {
            "id": o.id,
            "order_number": o.order_number,
            "total": float(o.total),
            "status": o.status,
            "is_paid": o.is_paid,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]
