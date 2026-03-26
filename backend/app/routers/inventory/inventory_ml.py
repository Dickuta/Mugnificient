from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rbac import require_permission, Permissions
from app.core.inventory_ml import InventoryML, get_inventory_ml
from app.models.models import User, Product, StockItem, RefillRequest

router = APIRouter(prefix="/inventory-ml", tags=["Inventory ML"])


class RefillApproval(BaseModel):
    approved: bool
    notes: Optional[str] = None


class RefillReceipt(BaseModel):
    actual_quantity: int
    actual_cost: Optional[float] = None


class RefillRequestCreate(BaseModel):
    product_id: int
    quantity_requested: int
    notes: Optional[str] = None
    supplier_id: Optional[int] = None


@router.get("/predictions")
def get_all_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_INVENTORY)),
):
    """Get inventory predictions for all products"""
    ml = get_inventory_ml(db)
    return ml.get_all_predictions()


@router.get("/predictions/{product_id}")
def get_product_prediction(
    product_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_INVENTORY)),
):
    """Get prediction for specific product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ml = get_inventory_ml(db)
    return ml.get_inventory_predictions(product_id, days)


@router.get("/refill-requests")
def get_refill_requests(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_INVENTORY)),
):
    """Get all refill requests"""
    query = db.query(RefillRequest).order_by(RefillRequest.requested_at.desc())

    if status:
        query = query.filter(RefillRequest.status == status)

    requests = query.all()

    return [
        {
            "id": r.id,
            "product_id": r.product_id,
            "product_name": r.product.name if r.product else None,
            "supplier_name": r.supplier.name if r.supplier else None,
            "quantity_requested": r.quantity_requested,
            "quantity_fulfilled": r.quantity_fulfilled,
            "status": r.status,
            "estimated_cost": float(r.estimated_cost) if r.estimated_cost else 0,
            "actual_cost": float(r.actual_cost) if r.actual_cost else None,
            "requested_at": r.requested_at.isoformat(),
            "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            "ordered_at": r.ordered_at.isoformat() if r.ordered_at else None,
            "received_at": r.received_at.isoformat() if r.received_at else None,
            "notes": r.notes,
        }
        for r in requests
    ]


@router.post("/refill-requests", response_model=dict)
def create_refill_request(
    request: RefillRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    """Create a new refill request"""
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    refill = RefillRequest(
        product_id=request.product_id,
        quantity_requested=request.quantity_requested,
        supplier_id=request.supplier_id,
        status="pending",
        notes=request.notes,
    )
    db.add(refill)
    db.commit()
    db.refresh(refill)
    
    return {
        "id": refill.id,
        "product_id": refill.product_id,
        "quantity_requested": refill.quantity_requested,
        "status": refill.status,
        "requested_at": refill.requested_at.isoformat() if refill.requested_at else None,
    }


@router.get("/refill-requests/{request_id}")
def get_refill_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_INVENTORY)),
):
    """Get specific refill request"""
    r = db.query(RefillRequest).filter(RefillRequest.id == request_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Refill request not found")

    return {
        "id": r.id,
        "product_id": r.product_id,
        "product_name": r.product.name if r.product else None,
        "supplier_name": r.supplier.name if r.supplier else None,
        "quantity_requested": r.quantity_requested,
        "quantity_fulfilled": r.quantity_fulfilled,
        "status": r.status,
        "estimated_cost": float(r.estimated_cost) if r.estimated_cost else 0,
        "requested_at": r.requested_at.isoformat(),
        "notes": r.notes,
    }


@router.post("/refill-requests/{request_id}/approve")
def approve_refill_request(
    request_id: int,
    approval: RefillApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    """Approve or reject a refill request"""
    r = db.query(RefillRequest).filter(RefillRequest.id == request_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Refill request not found")

    if not approval.approved:
        r.status = "cancelled"
        r.notes = (r.notes or "") + f"\nRejected by user {current_user.username}"
        if approval.notes:
            r.notes += f": {approval.notes}"
        db.commit()
        return {"message": "Refill request rejected"}

    r.status = "approved"
    r.approved_at = datetime.utcnow()
    if approval.notes:
        r.notes = (r.notes or "") + f"\nApproved: {approval.notes}"

    db.commit()
    return {"message": "Refill request approved"}


@router.post("/refill-requests/{request_id}/mark-ordered")
def mark_refill_ordered(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    """Mark refill as ordered"""
    r = db.query(RefillRequest).filter(RefillRequest.id == request_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Refill request not found")

    r.status = "ordered"
    r.ordered_at = datetime.utcnow()
    db.commit()

    return {"message": "Refill marked as ordered"}


@router.post("/refill-requests/{request_id}/receive")
def receive_refill(
    request_id: int,
    receipt: RefillReceipt,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    """Receive stock and close refill request"""
    ml = get_inventory_ml(db)

    try:
        result = ml.process_refill_receipt(
            request_id,
            receipt.actual_quantity,
            Decimal(str(receipt.actual_cost)) if receipt.actual_cost else None,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/refill-requests/{request_id}/cancel")
def cancel_refill_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    """Cancel a refill request"""
    r = db.query(RefillRequest).filter(RefillRequest.id == request_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Refill request not found")

    r.status = "cancelled"
    r.notes = (r.notes or "") + f"\nCancelled by {current_user.username}"
    db.commit()

    return {"message": "Refill request cancelled"}


@router.post("/trigger-stock-deduction/{order_id}")
def trigger_stock_deduction(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    """Manually trigger stock deduction for an order (for testing)"""
    ml = get_inventory_ml(db)
    result = ml.deduct_stock_on_purchase(order_id)
    return result
