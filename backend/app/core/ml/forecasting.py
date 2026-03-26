import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.models.models import (
    Product, SalesHistory, SeasonalPattern, StockItem, 
    Forecast, PurchaseOrder, PurchaseOrderItem, AutoOrderSettings
)

logger = logging.getLogger(__name__)


class ForecastingService:
    def __init__(self, db: Session):
        self.db = db

    def get_seasonal_multiplier(self, product_id: int, target_date: datetime) -> float:
        month = target_date.month
        pattern = (
            self.db.query(SeasonalPattern)
            .filter(SeasonalPattern.product_id == product_id)
            .filter(SeasonalPattern.month == month)
            .first()
        )
        return float(pattern.demand_multiplier) if pattern else 1.0

    def set_seasonal_pattern(
        self, product_id: int, month: int, multiplier: float, notes: str = ""
    ) -> SeasonalPattern:
        existing = (
            self.db.query(SeasonalPattern)
            .filter(SeasonalPattern.product_id == product_id)
            .filter(SeasonalPattern.month == month)
            .first()
        )
        
        if existing:
            existing.demand_multiplier = multiplier
            existing.notes = notes
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        pattern = SeasonalPattern(
            product_id=product_id,
            month=month,
            demand_multiplier=multiplier,
            notes=notes
        )
        self.db.add(pattern)
        self.db.commit()
        self.db.refresh(pattern)
        return pattern

    def record_sales(self, product_id: int, date: datetime, quantity: int, revenue: float = 0):
        existing = (
            self.db.query(SalesHistory)
            .filter(SalesHistory.product_id == product_id)
            .filter(func.date(SalesHistory.date) == date.date())
            .first()
        )
        
        if existing:
            existing.quantity_sold += quantity
            existing.revenue += revenue
        else:
            sales = SalesHistory(
                product_id=product_id,
                date=date,
                quantity_sold=quantity,
                revenue=revenue
            )
            self.db.add(sales)
        
        self.db.commit()

    def get_sales_history(self, product_id: int, days: int = 90) -> pd.DataFrame:
        cutoff = datetime.utcnow() - timedelta(days=days)
        sales = (
            self.db.query(SalesHistory)
            .filter(SalesHistory.product_id == product_id)
            .filter(SalesHistory.date >= cutoff)
            .order_by(SalesHistory.date)
            .all()
        )
        
        if not sales:
            return pd.DataFrame(columns=['date', 'quantity_sold', 'revenue'])
        
        data = [{
            'date': s.date,
            'quantity_sold': s.quantity_sold,
            'revenue': float(s.revenue)
        } for s in sales]
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df = df.resample('D').sum().fillna(0)
            df = df.reset_index()
        
        return df

    def forecast_demand(
        self, 
        product_id: int, 
        days_ahead: int = 30,
        include_seasonal: bool = True
    ) -> Dict:
        df = self.get_sales_history(product_id, days=90)
        
        stock = self.db.query(StockItem).filter(StockItem.product_id == product_id).first()
        current_stock = stock.quantity if stock else 0
        
        if df.empty or df['quantity_sold'].sum() == 0:
            avg_daily = 1
            trend = 0
        else:
            df['day_of_week'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            
            avg_daily = df['quantity_sold'].mean()
            trend = self._calculate_trend(df['quantity_sold'].values)
            
            weekly_pattern = df.groupby('day_of_week')['quantity_sold'].mean()
        
        seasonal_multipliers = {}
        if include_seasonal:
            patterns = (
                self.db.query(SeasonalPattern)
                .filter(SeasonalPattern.product_id == product_id)
                .all()
            )
            seasonal_multipliers = {p.month: float(p.demand_multiplier) for p in patterns}
        
        forecasts = []
        current_date = datetime.utcnow()
        
        for day in range(1, days_ahead + 1):
            forecast_date = current_date + timedelta(days=day)
            
            base_prediction = avg_daily * (1 + trend * day / 30)
            
            if include_seasonal:
                month = forecast_date.month
                month_multiplier = seasonal_multipliers.get(month, 1.0)
                base_prediction *= month_multiplier
            
            predicted_qty = max(0, int(base_prediction))
            
            confidence = 0.2 if df.empty else min(0.3, df['quantity_sold'].std() / (avg_daily + 1))
            confidence_interval = int(predicted_qty * confidence)
            
            forecasts.append({
                'date': forecast_date.isoformat(),
                'predicted_quantity': predicted_qty,
                'confidence_low': max(0, predicted_qty - confidence_interval),
                'confidence_high': predicted_qty + confidence_interval,
                'seasonal_factor': seasonal_multipliers.get(forecast_date.month, 1.0)
            })
        
        total_predicted = sum(f['predicted_quantity'] for f in forecasts)
        
        stock_depletion_date = None
        if avg_daily > 0:
            days_until_stockout = current_stock / avg_daily
            stock_depletion_date = (current_date + timedelta(days=days_until_stockout)).isoformat()
        
        recommended_order_date = None
        if current_stock < total_predicted * 0.3:
            lead_time_days = 7
            safety_stock = avg_daily * 7
            reorder_point = (avg_daily * lead_time_days) + safety_stock
            if current_stock < reorder_point:
                recommended_order_date = current_date.isoformat()
        
        return {
            'product_id': product_id,
            'current_stock': current_stock,
            'avg_daily_sales': round(avg_daily, 2),
            'trend': round(trend * 100, 2),
            'forecasts': forecasts,
            'total_predicted_demand': total_predicted,
            'stock_depletion_date': stock_depletion_date,
            'recommended_order_date': recommended_order_date,
            'seasonal_patterns': seasonal_multipliers
        }

    def _calculate_trend(self, values: np.ndarray) -> float:
        if len(values) < 7:
            return 0.0
        
        x = np.arange(len(values))
        try:
            coeffs = np.polyfit(x, values, 1)
            return coeffs[0] / (np.mean(values) + 1)
        except:
            return 0.0

    def save_forecast(
        self, 
        product_id: int, 
        forecast_date: datetime,
        predicted_quantity: int,
        confidence_low: int = 0,
        confidence_high: int = 0,
        is_auto_order: bool = False
    ) -> Forecast:
        existing = (
            self.db.query(Forecast)
            .filter(Forecast.product_id == product_id)
            .filter(func.date(Forecast.forecast_date) == forecast_date.date())
            .first()
        )
        
        if existing:
            existing.predicted_quantity = predicted_quantity
            existing.confidence_low = confidence_low
            existing.confidence_high = confidence_high
            existing.is_auto_order = is_auto_order
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        forecast = Forecast(
            product_id=product_id,
            forecast_date=forecast_date,
            predicted_quantity=predicted_quantity,
            confidence_low=confidence_low,
            confidence_high=confidence_high,
            is_auto_order=is_auto_order
        )
        self.db.add(forecast)
        self.db.commit()
        self.db.refresh(forecast)
        return forecast

    def get_forecast_summary(self, product_id: int, days: int = 30) -> List[Forecast]:
        cutoff = datetime.utcnow()
        return (
            self.db.query(Forecast)
            .filter(Forecast.product_id == product_id)
            .filter(Forecast.forecast_date >= cutoff)
            .filter(Forecast.forecast_date <= cutoff + timedelta(days=days))
            .order_by(Forecast.forecast_date)
            .all()
        )


class AutoOrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_settings(self, product_id: int) -> Optional[AutoOrderSettings]:
        return (
            self.db.query(AutoOrderSettings)
            .filter(AutoOrderSettings.product_id == product_id)
            .first()
        )

    def update_settings(
        self,
        product_id: int,
        enabled: bool,
        min_stock_threshold: int = 10,
        order_quantity: int = 50
    ) -> AutoOrderSettings:
        settings = self.get_settings(product_id)
        
        if settings:
            settings.enabled = enabled
            settings.min_stock_threshold = min_stock_threshold
            settings.order_quantity = order_quantity
        else:
            settings = AutoOrderSettings(
                product_id=product_id,
                enabled=enabled,
                min_stock_threshold=min_stock_threshold,
                order_quantity=order_quantity
            )
            self.db.add(settings)
        
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def create_purchase_order(
        self,
        supplier_id: int,
        items: List[Dict],
        is_auto_generated: bool = False,
        created_by: int = None,
        notes: str = ""
    ) -> PurchaseOrder:
        order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{np.random.randint(1000, 9999)}"
        
        total = sum(item['quantity'] * float(item.get('unit_cost', 0)) for item in items)
        
        order = PurchaseOrder(
            order_number=order_number,
            supplier_id=supplier_id,
            total_amount=total,
            notes=notes,
            is_auto_generated=is_auto_generated,
            created_by=created_by,
            status='pending' if is_auto_generated else 'pending'
        )
        self.db.add(order)
        self.db.flush()
        
        for item in items:
            po_item = PurchaseOrderItem(
                purchase_order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_cost=item.get('unit_cost', 0)
            )
            self.db.add(po_item)
        
        self.db.commit()
        self.db.refresh(order)
        return order

    def process_auto_orders(self) -> Dict:
        settings_list = self.db.query(AutoOrderSettings).filter(AutoOrderSettings.enabled == True).all()
        
        results = {
            'orders_created': 0,
            'orders': [],
            'skipped': []
        }
        
        for settings in settings_list:
            stock = self.db.query(StockItem).filter(StockItem.product_id == settings.product_id).first()
            current_stock = stock.quantity if stock else 0
            
            if current_stock >= settings.min_stock_threshold:
                results['skipped'].append({
                    'product_id': settings.product_id,
                    'reason': 'stock_adequate'
                })
                continue
            
            product = self.db.query(Product).filter(Product.id == settings.product_id).first()
            if not product:
                continue
            
            supplier_id = stock.supplier_id if stock else None
            
            order = self.create_purchase_order(
                supplier_id=supplier_id,
                items=[{
                    'product_id': settings.product_id,
                    'quantity': settings.order_quantity,
                    'unit_cost': float(stock.unit_cost) if stock and stock.unit_cost else 0
                }],
                is_auto_generated=True,
                notes=f"Auto-generated order based on stock forecast. Current stock: {current_stock}"
            )
            
            results['orders_created'] += 1
            results['orders'].append({
                'order_number': order.order_number,
                'product_id': settings.product_id,
                'quantity': settings.order_quantity
            })
        
        self.db.commit()
        return results

    def get_purchase_orders(self, status: str = None) -> List[PurchaseOrder]:
        query = self.db.query(PurchaseOrder)
        if status:
            query = query.filter(PurchaseOrder.status == status)
        return query.order_by(PurchaseOrder.created_at.desc()).all()
    
    def get_purchase_order_by_id(self, order_id: int) -> PurchaseOrder:
        return self.db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    
    def update_po_status(self, order_id: int, status: str) -> PurchaseOrder:
        order = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not order:
            return None
        
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order
