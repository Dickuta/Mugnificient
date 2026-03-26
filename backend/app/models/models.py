from .user.models import (
    Permission, Role, UserRole, User
)
from .ecommerce.models import (
    Address, Category, Product, Review, Cart, CartItem, 
    Order, OrderItem, Payment
)
from .inventory.models import (
    Supplier, StockItem, StockMovement, RestockAlert, RefillRequest,
    SeasonalPattern, SalesHistory, Forecast, PurchaseOrder, PurchaseOrderItem,
    AutoOrderSettings
)

__all__ = [
    'Permission', 'Role', 'UserRole', 'User',
    'Address', 'Category', 'Product', 'Review', 
    'Cart', 'CartItem', 'Order', 'OrderItem', 'Payment',
    'Supplier', 'StockItem', 'StockMovement', 'RestockAlert', 'RefillRequest',
    'SeasonalPattern', 'SalesHistory', 'Forecast', 'PurchaseOrder', 
    'PurchaseOrderItem', 'AutoOrderSettings'
]


class RefillRequest(Base):
    __tablename__ = "refill_requests"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    quantity_requested = Column(Integer, default=0)
    quantity_fulfilled = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, approved, ordered, received, cancelled
    estimated_cost = Column(Decimal(10, 2), default=0)
    actual_cost = Column(Decimal(10, 2), nullable=True)
    notes = Column(Text, default="")
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    ordered_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)

    product = relationship("Product")
    supplier = relationship("Supplier")


class SeasonalPattern(Base):
    __tablename__ = "seasonal_patterns"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    demand_multiplier = Column(Decimal(5, 2), default=1.0)  # 1.0 = normal, >1 = high season, <1 = low season
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product")


class SalesHistory(Base):
    __tablename__ = "sales_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    quantity_sold = Column(Integer, default=0)
    revenue = Column(Decimal(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    predicted_quantity = Column(Integer, nullable=False)
    confidence_low = Column(Integer, default=0)
    confidence_high = Column(Integer, default=0)
    is_auto_order = Column(Boolean, default=False)
    auto_order_created = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    status = Column(String(20), default="pending")  # pending, ordered, received, cancelled
    total_amount = Column(Decimal(10, 2), default=0)
    notes = Column(Text, default="")
    expected_delivery = Column(DateTime, nullable=True)
    is_auto_generated = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier")
    items = relationship("PurchaseOrderItem", back_populates="order")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Decimal(10, 2), default=0)
    received_quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")


class AutoOrderSettings(Base):
    __tablename__ = "auto_order_settings"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True)
    enabled = Column(Boolean, default=False)
    min_stock_threshold = Column(Integer, default=10)
    order_quantity = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product")
