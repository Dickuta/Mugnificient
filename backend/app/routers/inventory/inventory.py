from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rbac import require_permission, Permissions
from app.models.models import (
    User,
    Product,
    Supplier,
    StockItem,
    StockMovement,
    RestockAlert,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/dashboard")
def get_inventory_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_INVENTORY)),
):
    total_products = db.query(Product).filter(Product.is_active == True).count()
    low_stock_count = (
        db.query(StockItem)
        .filter(StockItem.quantity <= StockItem.reorder_level)
        .count()
    )
    out_of_stock_count = db.query(StockItem).filter(StockItem.quantity <= 0).count()
    total_value = (
        db.query(func.sum(StockItem.quantity * StockItem.unit_cost)).scalar() or 0
    )

    # Recent stock movements
    recent_movements = (
        db.query(StockMovement)
        .order_by(StockMovement.created_at.desc())
        .limit(10)
        .all()
    )

    # Active alerts
    active_alerts = (
        db.query(RestockAlert)
        .filter(RestockAlert.is_active == True, RestockAlert.is_resolved == False)
        .count()
    )

    return {
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "total_inventory_value": float(total_value),
        "active_alerts": active_alerts,
        "recent_movements": [
            {
                "id": m.id,
                "product_id": m.stock_item.product_id if m.stock_item else None,
                "product_name": m.stock_item.product.name
                if m.stock_item and m.stock_item.product
                else None,
                "quantity_change": m.quantity_change,
                "movement_type": m.movement_type,
                "notes": m.notes,
                "created_at": m.created_at.isoformat(),
            }
            for m in recent_movements
        ],
    }


@router.get("/products")
def get_inventory_products(
    low_stock: bool = False,
    out_of_stock: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_INVENTORY)),
):
    query = (
        db.query(Product, StockItem)
        .outerjoin(StockItem, Product.id == StockItem.product_id)
        .filter(Product.is_active == True)
    )

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    results = query.all()

    inventory = []
    for product, stock in results:
        qty = stock.quantity if stock else 0
        reorder_level = stock.reorder_level if stock else 10

        if low_stock and qty > reorder_level:
            continue
        if out_of_stock and qty > 0:
            continue

        inventory.append(
            {
                "id": product.id,
                "name": product.name,
                "sku": product.sku,
                "category": product.category.name if product.category else None,
                "current_stock": qty,
                "reorder_level": reorder_level,
                "reorder_quantity": stock.reorder_quantity if stock else 50,
                "unit_cost": float(stock.unit_cost) if stock and stock.unit_cost else 0,
                "last_restocked": stock.last_restocked.isoformat()
                if stock and stock.last_restocked
                else None,
                "is_low_stock": qty <= reorder_level,
                "is_out_of_stock": qty <= 0,
            }
        )

    return inventory


@router.get("/products/{product_id}")
def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_INVENTORY)),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stock = db.query(StockItem).filter(StockItem.product_id == product_id).first()

    # Get stock history
    movements = (
        db.query(StockMovement)
        .join(StockItem)
        .filter(StockItem.product_id == product_id)
        .order_by(StockMovement.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "product": {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "stock": product.stock,
        },
        "stock": {
            "quantity": stock.quantity if stock else 0,
            "reorder_level": stock.reorder_level if stock else 10,
            "reorder_quantity": stock.reorder_quantity if stock else 50,
            "unit_cost": float(stock.unit_cost) if stock and stock.unit_cost else 0,
            "last_restocked": stock.last_restocked.isoformat()
            if stock and stock.last_restocked
            else None,
            "supplier": stock.supplier.name if stock and stock.supplier else None,
        }
        if stock
        else None,
        "movements": [
            {
                "id": m.id,
                "quantity_change": m.quantity_change,
                "movement_type": m.movement_type,
                "notes": m.notes,
                "created_at": m.created_at.isoformat(),
            }
            for m in movements
        ],
    }


@router.post("/stock/adjust")
def adjust_stock(
    product_id: int,
    quantity_change: int,
    movement_type: str,  # 'in', 'out', 'adjustment'
    notes: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get or create stock item
    stock = db.query(StockItem).filter(StockItem.product_id == product_id).first()
    if not stock:
        stock = StockItem(product_id=product_id, quantity=product.stock)
        db.add(stock)
        db.flush()

    # Update quantity
    old_qty = stock.quantity
    stock.quantity = max(0, stock.quantity + quantity_change)

    if movement_type == "in":
        stock.last_restocked = datetime.utcnow()

    # Create movement record
    movement = StockMovement(
        stock_item_id=stock.id,
        quantity_change=quantity_change,
        movement_type=movement_type,
        notes=notes,
        created_by=current_user.id,
    )
    db.add(movement)

    # Update product stock
    product.stock = stock.quantity

    # Check for low stock alert
    if stock.quantity <= stock.reorder_level:
        existing_alert = (
            db.query(RestockAlert)
            .filter(
                RestockAlert.product_id == product_id,
                RestockAlert.is_active == True,
                RestockAlert.is_resolved == False,
            )
            .first()
        )

        if not existing_alert:
            alert = RestockAlert(product_id=product_id)
            db.add(alert)

    db.commit()
    db.refresh(stock)

    return {
        "message": "Stock adjusted successfully",
        "previous_quantity": old_qty,
        "new_quantity": stock.quantity,
    }


@router.get("/alerts")
def get_restock_alerts(
    include_resolved: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_STOCK_ALERTS)),
):
    query = db.query(RestockAlert, Product).join(
        Product, RestockAlert.product_id == Product.id
    )

    if not include_resolved:
        query = query.filter(RestockAlert.is_resolved == False)

    alerts = query.order_by(RestockAlert.created_at.desc()).all()

    return [
        {
            "id": alert.id,
            "product_id": product.id,
            "product_name": product.name,
            "current_stock": product.stock,
            "is_active": alert.is_active,
            "is_resolved": alert.is_resolved,
            "notes": alert.notes,
            "created_at": alert.created_at.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        }
        for alert, product in alerts
    ]


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    notes: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    alert = db.query(RestockAlert).filter(RestockAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_resolved = True
    alert.is_active = False
    alert.resolved_at = datetime.utcnow()
    if notes:
        alert.notes = notes

    db.commit()

    return {"message": "Alert resolved"}


# Suppliers
@router.get("/suppliers")
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_SUPPLIERS)),
):
    suppliers = db.query(Supplier).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "phone": s.phone,
            "contact_person": s.contact_person,
            "address": s.address,
            "is_active": s.is_active,
        }
        for s in suppliers
    ]


@router.post("/suppliers")
def create_supplier(
    name: str,
    email: str = "",
    phone: str = "",
    contact_person: str = "",
    address: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_SUPPLIERS)),
):
    supplier = Supplier(
        name=name,
        email=email,
        phone=phone,
        contact_person=contact_person,
        address=address,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return {"id": supplier.id, "name": supplier.name}


@router.put("/suppliers/{supplier_id}")
def update_supplier(
    supplier_id: int,
    name: str = None,
    email: str = None,
    phone: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_SUPPLIERS)),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    if name is not None:
        supplier.name = name
    if email is not None:
        supplier.email = email
    if phone is not None:
        supplier.phone = phone
    if is_active is not None:
        supplier.is_active = is_active

    db.commit()
    return {"message": "Supplier updated"}


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_SUPPLIERS)),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted"}
