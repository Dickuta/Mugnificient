from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rbac import require_permission, Permissions
from app.core.forecasting import ForecastingService, AutoOrderService
from app.models.models import User, Product

router = APIRouter(
    prefix="/forecasting",
    tags=["forecasting"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not found - Resource does not exist"},
    }
)


class SeasonalPatternCreate(BaseModel):
    month: int
    demand_multiplier: float
    notes: str = ""


class SeasonalPatternResponse(BaseModel):
    id: int
    product_id: int
    month: int
    demand_multiplier: float
    notes: str


class ForecastResponse(BaseModel):
    product_id: int
    current_stock: int
    avg_daily_sales: float
    trend: float
    forecasts: List[dict]
    total_predicted_demand: int
    stock_depletion_date: Optional[str]
    recommended_order_date: Optional[str]
    seasonal_patterns: dict


class AutoOrderSettingsUpdate(BaseModel):
    enabled: bool
    min_stock_threshold: int = 10
    order_quantity: int = 50


class AutoOrderSettingsResponse(BaseModel):
    product_id: int
    enabled: bool
    min_stock_threshold: int
    order_quantity: int


class PurchaseOrderCreate(BaseModel):
    supplier_id: Optional[int] = None
    items: List[dict]
    notes: str = ""


class PurchaseOrderResponse(BaseModel):
    id: int
    order_number: str
    supplier_id: Optional[int]
    status: str
    total_amount: float
    notes: str
    is_auto_generated: bool
    created_at: str


@router.get(
    "/products/{product_id}/forecast",
    response_model=ForecastResponse,
    summary="Get demand forecast for a product",
    description="""
    Generate a demand forecast for a specific product based on historical sales data.
    
    The forecast includes:
    - Predicted daily demand for the next N days
    - Seasonal adjustments if enabled
    - Confidence intervals
    - Stock depletion date estimation
    - Recommended order date
    
    **Seasonal patterns**: Use the seasonal-patterns endpoint to configure monthly demand multipliers.
    For example, set September-November to 1.5 for university intake season.
    """
)
def get_forecast(
    product_id: int,
    days_ahead: int = Query(default=30, ge=1, le=365, description="Number of days to forecast"),
    include_seasonal: bool = Query(default=True, description="Apply seasonal adjustments to forecast"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_FORECASTS)),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    forecasting = ForecastingService(db)
    result = forecasting.forecast_demand(product_id, days_ahead, include_seasonal)
    
    for fc in result['forecasts']:
        forecasting.save_forecast(
            product_id=product_id,
            forecast_date=datetime.fromisoformat(fc['date']),
            predicted_quantity=fc['predicted_quantity'],
            confidence_low=fc['confidence_low'],
            confidence_high=fc['confidence_high']
        )
    
    return result


@router.get("/products/{product_id}/seasonal-patterns")
def get_seasonal_patterns(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_SEASONAL_PATTERNS)),
):
    from app.models.models import SeasonalPattern
    patterns = (
        db.query(SeasonalPattern)
        .filter(SeasonalPattern.product_id == product_id)
        .all()
    )
    return [
        {
            "id": p.id,
            "month": p.month,
            "demand_multiplier": float(p.demand_multiplier),
            "notes": p.notes
        }
        for p in patterns
    ]


@router.post("/products/{product_id}/seasonal-patterns")
def set_seasonal_pattern(
    product_id: int,
    pattern: SeasonalPatternCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_SEASONAL_PATTERNS)),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if pattern.month < 1 or pattern.month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    forecasting = ForecastingService(db)
    result = forecasting.set_seasonal_pattern(
        product_id, pattern.month, pattern.demand_multiplier, pattern.notes
    )
    
    return {
        "id": result.id,
        "product_id": result.product_id,
        "month": result.month,
        "demand_multiplier": float(result.demand_multiplier),
        "notes": result.notes
    }


@router.post("/products/{product_id}/record-sales")
def record_sales(
    product_id: int,
    quantity: int,
    revenue: float = 0,
    date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_FORECASTS)),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    forecasting = ForecastingService(db)
    forecasting.record_sales(
        product_id,
        date or datetime.utcnow(),
        quantity,
        revenue
    )
    
    return {"message": "Sales recorded successfully"}


@router.get("/dashboard")
def get_forecasting_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_FORECASTS)),
):
    products = db.query(Product).filter(Product.is_active == True).all()
    
    forecasting = ForecastingService(db)
    results = []
    
    for product in products:
        forecast = forecasting.forecast_demand(product.id, days_ahead=30, include_seasonal=True)
        results.append({
            "product_id": product.id,
            "product_name": product.name,
            "current_stock": forecast["current_stock"],
            "avg_daily_sales": forecast["avg_daily_sales"],
            "total_predicted_demand": forecast["total_predicted_demand"],
            "stock_depletion_date": forecast["stock_depletion_date"],
            "recommended_order_date": forecast["recommended_order_date"],
            "needs_attention": forecast["recommended_order_date"] is not None
        })
    
    needs_attention = [r for r in results if r["needs_attention"]]
    
    return {
        "products": results,
        "products_needing_attention": len(needs_attention),
        "total_products": len(results)
    }


@router.get("/auto-order/settings/{product_id}", response_model=AutoOrderSettingsResponse)
def get_auto_order_settings(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_FORECASTS)),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    auto_order = AutoOrderService(db)
    settings = auto_order.get_settings(product_id)
    
    if not settings:
        return {
            "product_id": product_id,
            "enabled": False,
            "min_stock_threshold": 10,
            "order_quantity": 50
        }
    
    return {
        "product_id": settings.product_id,
        "enabled": settings.enabled,
        "min_stock_threshold": settings.min_stock_threshold,
        "order_quantity": settings.order_quantity
    }


@router.put("/auto-order/settings/{product_id}")
def update_auto_order_settings(
    product_id: int,
    settings: AutoOrderSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_AUTO_ORDERS)),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    auto_order = AutoOrderService(db)
    result = auto_order.update_settings(
        product_id,
        settings.enabled,
        settings.min_stock_threshold,
        settings.order_quantity
    )
    
    return {
        "product_id": result.product_id,
        "enabled": result.enabled,
        "min_stock_threshold": result.min_stock_threshold,
        "order_quantity": result.order_quantity
    }


@router.post("/auto-order/process")
def process_auto_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_AUTO_ORDERS)),
):
    auto_order = AutoOrderService(db)
    results = auto_order.process_auto_orders()
    return results


@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
def get_purchase_orders(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_PURCHASE_ORDERS)),
):
    auto_order = AutoOrderService(db)
    orders = auto_order.get_purchase_orders(status)
    
    return [
        {
            "id": o.id,
            "order_number": o.order_number,
            "supplier_id": o.supplier_id,
            "status": o.status,
            "total_amount": float(o.total_amount),
            "notes": o.notes,
            "is_auto_generated": o.is_auto_generated,
            "created_at": o.created_at.isoformat()
        }
        for o in orders
    ]


@router.get("/purchase-orders/{order_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.VIEW_PURCHASE_ORDERS)),
):
    """Get specific purchase order"""
    from app.core.forecasting import AutoOrderService
    auto_order = AutoOrderService(db)
    order = auto_order.get_purchase_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "supplier_id": order.supplier_id,
        "status": order.status,
        "total_amount": float(order.total_amount),
        "notes": order.notes,
        "is_auto_generated": order.is_auto_generated,
        "created_at": order.created_at.isoformat()
    }


@router.post("/purchase-orders", response_model=PurchaseOrderResponse)
def create_purchase_order(
    order: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_PURCHASE_ORDERS)),
):
    if not order.items:
        raise HTTPException(status_code=400, detail="At least one item is required")
    
    auto_order = AutoOrderService(db)
    result = auto_order.create_purchase_order(
        supplier_id=order.supplier_id,
        items=order.items,
        is_auto_generated=False,
        created_by=current_user.id,
        notes=order.notes
    )
    
    return {
        "id": result.id,
        "order_number": result.order_number,
        "supplier_id": result.supplier_id,
        "status": result.status,
        "total_amount": float(result.total_amount),
        "notes": result.notes,
        "is_auto_generated": result.is_auto_generated,
        "created_at": result.created_at.isoformat()
    }


@router.patch("/purchase-orders/{order_id}")
def update_purchase_order(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_PURCHASE_ORDERS)),
):
    valid_statuses = ["pending", "ordered", "received", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")
    
    auto_order = AutoOrderService(db)
    order = auto_order.update_po_status(order_id, status)
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status
    }
