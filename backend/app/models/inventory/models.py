from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.data.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact_name = Column(String(200), default="")
    email = Column(String(255), default="")
    phone = Column(String(20), default="")
    address = Column(String(255), default="")
    city = Column(String(100), default="")
    state = Column(String(100), default="")
    zip_code = Column(String(20), default="")
    country = Column(String(100), default="United States")
    is_active = Column(Boolean, default=True)
    notes = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StockItem(Base):
    __tablename__ = "stock_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    current_quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)  # for pending orders
    available_quantity = Column(Integer, default=0)  # current - reserved
    min_stock_level = Column(Integer, default=10)
    max_stock_level = Column(Integer, default=1000)
    unit_cost = Column(Decimal(10, 2), default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    last_count_date = Column(DateTime, nullable=True)
    notes = Column(String(500), default="")

    # Relationships
    product = relationship("Product")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    movement_type = Column(String(20), nullable=False)  # 'in', 'out', 'adjustment'
    quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50))  # 'order', 'return', 'adjustment', 'purchase_order'
    reference_id = Column(Integer)  # ID of the related order/PO
    notes = Column(String(500), default="")
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product")
    user = relationship("User")


class RestockAlert(Base):
    __tablename__ = "restock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    current_stock = Column(Integer, nullable=False)
    threshold = Column(Integer, nullable=False)
    message = Column(String(500), nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product")
    user = relationship("User")


class RefillRequest(Base):
    __tablename__ = "refill_requests"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    quantity_requested = Column(Integer, default=0)
    quantity_fulfilled = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, approved, ordered, received, cancelled
    estimated_cost = Column(Decimal(10, 2), default=0)
    actual_cost = Column(Decimal(10, 2), nullable=True)
    notes = Column(String(500), default="")
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    ordered_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    product = relationship("Product")
    supplier = relationship("Supplier")
    user = relationship("User")


class SeasonalPattern(Base):
    __tablename__ = "seasonal_patterns"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    month = Column(Integer, nullable=False)  # 1-12
    demand_multiplier = Column(Decimal(5, 2), default=1.0)  # e.g., 1.5 for 50% higher demand
    notes = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product")


class SalesHistory(Base):
    __tablename__ = "sales_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    date = Column(DateTime, nullable=False)
    quantity_sold = Column(Integer, default=0)
    revenue = Column(Decimal(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product")


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    forecast_date = Column(DateTime, nullable=False)
    predicted_quantity = Column(Integer, nullable=False)
    confidence_low = Column(Integer, default=0)
    confidence_high = Column(Integer, default=0)
    is_auto_order = Column(Boolean, default=False)
    auto_order_created = Column(Boolean, default=False)  # Whether auto-order was generated
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    status = Column(String(20), default="pending")  # pending, approved, shipped, delivered, cancelled
    total_amount = Column(Decimal(10, 2), default=0)
    notes = Column(String(500), default="")
    expected_delivery = Column(DateTime, nullable=True)
    is_auto_generated = Column(Boolean, default=False)  # Generated by ML system
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier")
    user = relationship("User")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Decimal(10, 2), default=0)
    received_quantity = Column(Integer, default=0)  # Quantity actually received
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")


# Add back_populates to the PurchaseOrder relationship
PurchaseOrder.items = relationship("PurchaseOrderItem", back_populates="purchase_order")


class AutoOrderSettings(Base):
    __tablename__ = "auto_order_settings"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    enabled = Column(Boolean, default=False)
    min_stock_threshold = Column(Integer, default=10)
    order_quantity = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product")