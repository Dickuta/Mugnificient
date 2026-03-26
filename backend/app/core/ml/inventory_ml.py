import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import (
    Product,
    StockItem,
    StockMovement,
    RestockAlert,
    RefillRequest,
    Supplier,
    Order,
    OrderItem,
)
from app.core.emails import send_restock_alert

logger = logging.getLogger(__name__)


class InventoryML:
    """
    ML-powered inventory management system
    - Tracks stock levels
    - Predicts restock needs
    - Auto-generates refill requests
    """

    LOW_STOCK_THRESHOLD = 20

    def __init__(self, db: Session):
        self.db = db

    def deduct_stock_on_purchase(self, order_id: int) -> Dict:
        """
        Deduct stock when order is placed
        Returns: dict with updated products and any alerts triggered
        """
        result = {
            "order_id": order_id,
            "items_updated": [],
            "alerts_created": [],
            "refill_requests": [],
        }

        order_items = (
            self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        )

        for item in order_items:
            product = (
                self.db.query(Product).filter(Product.id == item.product_id).first()
            )

            if not product:
                continue

            stock = (
                self.db.query(StockItem)
                .filter(StockItem.product_id == item.product_id)
                .first()
            )

            if not stock:
                stock = StockItem(
                    product_id=item.product_id,
                    quantity=product.stock,
                    reorder_level=self.LOW_STOCK_THRESHOLD,
                )
                self.db.add(stock)
                self.db.flush()

            old_quantity = stock.quantity
            stock.quantity = max(0, stock.quantity - item.quantity)

            movement = StockMovement(
                stock_item_id=stock.id,
                quantity_change=-item.quantity,
                movement_type="out",
                notes=f"Order #{order_id}",
            )
            self.db.add(movement)

            result["items_updated"].append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "old_quantity": old_quantity,
                    "new_quantity": stock.quantity,
                    "deducted": item.quantity,
                }
            )

            if stock.quantity <= stock.reorder_level:
                alert = self.check_and_create_alert(product.id, stock.quantity)
                if alert:
                    result["alerts_created"].append(alert)

                    refill = self.auto_generate_refill(product.id, stock.id)
                    if refill:
                        result["refill_requests"].append(refill)

        self.db.commit()
        return result

    def check_and_create_alert(
        self, product_id: int, current_stock: int
    ) -> Optional[Dict]:
        """Check stock level and create alert if below threshold"""

        existing = (
            self.db.query(RestockAlert)
            .filter(
                RestockAlert.product_id == product_id,
                RestockAlert.is_active == True,
                RestockAlert.is_resolved == False,
            )
            .first()
        )

        if existing:
            return None

        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        alert = RestockAlert(
            product_id=product_id,
            is_active=True,
            notes=f"Auto-generated: Stock below threshold (current: {current_stock})",
        )
        self.db.add(alert)
        self.db.flush()

        admin_email = os.getenv("ADMIN_EMAIL", "admin@mugstore.com")
        try:
            send_restock_alert(
                to_email=admin_email,
                product_name=product.name,
                current_stock=current_stock,
            )
            alert.notes += " - Email sent"
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

        self.db.commit()

        return {
            "product_id": product_id,
            "product_name": product.name,
            "current_stock": current_stock,
            "alert_id": alert.id,
        }

    def auto_generate_refill(self, product_id: int, stock_id: int) -> Optional[Dict]:
        """Automatically generate refill request when stock is low"""

        product = self.db.query(Product).filter(Product.id == product_id).first()
        stock = self.db.query(StockItem).filter(StockItem.id == stock_id).first()

        if not product or not stock:
            return None

        existing = (
            self.db.query(RefillRequest)
            .filter(
                RefillRequest.product_id == product_id,
                RefillRequest.status.in_(["pending", "approved", "ordered"]),
            )
            .first()
        )

        if existing:
            return None

        reorder_qty = stock.reorder_quantity or 50
        target_stock = 100
        refill_qty = max(reorder_qty, target_stock - stock.quantity)

        supplier = None
        if stock.supplier_id:
            supplier = (
                self.db.query(Supplier)
                .filter(Supplier.id == stock.supplier_id, Supplier.is_active == True)
                .first()
            )

        unit_cost = stock.unit_cost or Decimal(str(float(product.price) * 0.4))
        estimated_cost = unit_cost * refill_qty

        refill = RefillRequest(
            product_id=product_id,
            supplier_id=supplier.id if supplier else None,
            quantity_requested=refill_qty,
            status="pending",
            estimated_cost=estimated_cost,
            notes=f"Auto-generated: Low stock alert triggered (current: {stock.quantity}, reorder level: {stock.reorder_level})",
        )

        self.db.add(refill)
        self.db.commit()
        self.db.refresh(refill)

        return {
            "refill_id": refill.id,
            "product_name": product.name,
            "quantity_requested": refill_qty,
            "estimated_cost": float(estimated_cost),
            "supplier": supplier.name if supplier else "Not assigned",
        }

    def get_inventory_predictions(self, product_id: int, days: int = 30) -> Dict:
        """
        ML-based prediction: Estimate when product will run out
        Based on historical sales velocity
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        sales = (
            self.db.query(func.sum(OrderItem.quantity))
            .join(Order)
            .filter(
                OrderItem.product_id == product_id,
                Order.is_paid == True,
                Order.created_at >= start_date,
            )
            .scalar()
            or 0
        )

        daily_avg = sales / days if days > 0 else 0

        stock = (
            self.db.query(StockItem).filter(StockItem.product_id == product_id).first()
        )

        current_stock = stock.quantity if stock else 0

        if daily_avg > 0:
            days_until_stockout = current_stock / daily_avg
            predicted_stockout_date = datetime.utcnow() + timedelta(
                days=days_until_stockout
            )
        else:
            days_until_stockout = None
            predicted_stockout_date = None

        if current_stock <= 0:
            risk_level = "critical"
        elif current_stock <= 10:
            risk_level = "high"
        elif current_stock <= 20:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "product_id": product_id,
            "current_stock": current_stock,
            "sales_last_30_days": sales,
            "daily_average_sales": round(daily_avg, 2),
            "days_until_stockout": round(days_until_stockout, 1)
            if days_until_stockout
            else None,
            "predicted_stockout_date": predicted_stockout_date.isoformat()
            if predicted_stockout_date
            else None,
            "risk_level": risk_level,
            "recommended_order_quantity": max(50, int(daily_avg * 30))
            if daily_avg > 0
            else 50,
        }

    def get_all_predictions(self) -> List[Dict]:
        """Get predictions for all products"""
        products = self.db.query(Product).filter(Product.is_active == True).all()

        predictions = []
        for product in products:
            pred = self.get_inventory_predictions(product.id)
            pred["product_name"] = product.name
            predictions.append(pred)

        risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        predictions.sort(key=lambda x: risk_order.get(x["risk_level"], 4))

        return predictions

    def process_refill_receipt(
        self, refill_id: int, actual_quantity: int, actual_cost: Decimal = None
    ):
        """Process received stock from refill request"""
        refill = (
            self.db.query(RefillRequest).filter(RefillRequest.id == refill_id).first()
        )

        if not refill:
            raise ValueError("Refill request not found")

        refill.quantity_fulfilled = actual_quantity
        refill.status = "received"
        refill.received_at = datetime.utcnow()

        if actual_cost:
            refill.actual_cost = actual_cost

        stock = (
            self.db.query(StockItem)
            .filter(StockItem.product_id == refill.product_id)
            .first()
        )

        if stock:
            stock.quantity += actual_quantity
            stock.last_restocked = datetime.utcnow()

            movement = StockMovement(
                stock_item_id=stock.id,
                quantity_change=actual_quantity,
                movement_type="in",
                notes=f"Refill request #{refill_id} received",
            )
            self.db.add(movement)

        alerts = (
            self.db.query(RestockAlert)
            .filter(
                RestockAlert.product_id == refill.product_id,
                RestockAlert.is_active == True,
                RestockAlert.is_resolved == False,
            )
            .all()
        )

        for alert in alerts:
            alert.is_resolved = True
            alert.is_active = False
            alert.resolved_at = datetime.utcnow()
            alert.notes += f" - Stock replenished via refill #{refill_id}"

        self.db.commit()

        return {
            "refill_id": refill_id,
            "quantity_received": actual_quantity,
            "new_stock_level": stock.quantity if stock else 0,
        }


def get_inventory_ml(db: Session) -> InventoryML:
    """Factory function to get InventoryML instance"""
    return InventoryML(db)
