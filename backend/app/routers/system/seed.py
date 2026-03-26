from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rbac import require_permission, Permissions
from app.core.forecasting import ForecastingService
from app.models.models import User, Product, SalesHistory

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/forecasting")
def seed_forecasting_data(
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_FORECASTS)),
):
    products = db.query(Product).filter(Product.is_active == True).all()
    
    if not products:
        raise HTTPException(status_code=400, detail="No products found. Please create products first.")
    
    forecasting = ForecastingService(db)
    
    seeded_sales = 0
    seeded_patterns = 0
    
    for product in products:
        base_daily = random.randint(1, 10)
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days - i)
            
            day_of_week = date.weekday()
            weekday_multiplier = 1.0
            if day_of_week >= 5:
                weekday_multiplier = 0.5
            
            month = date.month
            month_multiplier = 1.0
            if month in [9, 10, 11]:
                month_multiplier = 1.5
            elif month in [12, 1, 2]:
                month_multiplier = 0.7
            
            variation = random.uniform(0.7, 1.3)
            quantity = int(base_daily * weekday_multiplier * month_multiplier * variation)
            quantity = max(0, quantity)
            
            revenue = quantity * random.uniform(8, 25)
            
            forecasting.record_sales(
                product_id=product.id,
                date=date,
                quantity=quantity,
                revenue=revenue
            )
            seeded_sales += 1
        
        seasonal_patterns = {
            1: 0.8,
            2: 0.8,
            3: 1.0,
            4: 1.0,
            5: 1.1,
            6: 1.2,
            7: 1.3,
            8: 1.2,
            9: 1.5,
            10: 1.6,
            11: 1.8,
            12: 1.4
        }
        
        for month, multiplier in seasonal_patterns.items():
            forecasting.set_seasonal_pattern(
                product_id=product.id,
                month=month,
                multiplier=multiplier,
                notes=f"Seasonal pattern for month {month}"
            )
            seeded_patterns += 1
    
    return {
        "message": "Sample forecasting data seeded successfully",
        "sales_records": seeded_sales,
        "seasonal_patterns": seeded_patterns,
        "products_processed": len(products)
    }


@router.post("/stock")
def seed_stock_data(
    min_stock: int = 20,
    max_stock: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_INVENTORY)),
):
    from app.models.models import StockItem
    
    products = db.query(Product).filter(Product.is_active == True).all()
    
    seeded = 0
    for product in products:
        stock = db.query(StockItem).filter(StockItem.product_id == product.id).first()
        
        if not stock:
            stock = StockItem(
                product_id=product.id,
                quantity=random.randint(min_stock, max_stock),
                reorder_level=random.randint(5, 15),
                reorder_quantity=random.randint(30, 60),
                unit_cost=random.uniform(5, 15)
            )
            db.add(stock)
        else:
            stock.quantity = random.randint(min_stock, max_stock)
        
        product.stock = stock.quantity
        seeded += 1
    
    db.commit()
    
    return {
        "message": "Stock data seeded successfully",
        "products_updated": seeded
    }
