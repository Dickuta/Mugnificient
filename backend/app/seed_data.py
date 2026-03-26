"""
Comprehensive Seed Data for Production-Like Testing
=================================================

This script creates a realistic Mugnificent e-commerce system with:
- Multiple user roles and permissions
- Rich product catalog with images
- Historical sales data (180 days)
- Realistic seasonal patterns
- Existing orders in various states
- Active alerts and refill requests
- Complete supplier data

Run: python -m app.seed_data
"""
import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.security import get_password_hash
from app.core.forecasting import ForecastingService
from app.models.models import (
    User, Role, Category, Product, Supplier, StockItem, StockMovement,
    SalesHistory, SeasonalPattern, Order, OrderItem, Cart, CartItem,
    RestockAlert, RefillRequest
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mugnificent.db")

# =============================================================================
# REALISTIC PRODUCT CATALOG
# =============================================================================
PRODUCTS = [
    # Classic Mugs
    {"name": "UoS Classic Ceramic Mug", "price": 12.99, "stock": 85, "category": "Classic"},
    {"name": "UoS Matte Black Mug", "price": 14.99, "stock": 45, "category": "Classic"},
    {"name": "UoS Stoneware Mug", "price": 16.99, "stock": 32, "category": "Classic"},
    {"name": "UoS Enamel Camp Mug", "price": 11.99, "stock": 60, "category": "Classic"},
    
    # Travel Mugs
    {"name": "UoS Thermal Travel Mug", "price": 22.99, "stock": 28, "category": "Travel"},
    {"name": "UoS Insulated Tumbler", "price": 19.99, "stock": 52, "category": "Travel"},
    {"name": "UoS Ceramic Travel Cup", "price": 15.99, "stock": 40, "category": "Travel"},
    
    # Sports & Outdoor
    {"name": "UoS Sports Bottle 500ml", "price": 14.99, "stock": 75, "category": "Sports"},
    {"name": "UoS Gym Shaker", "price": 12.99, "stock": 38, "category": "Sports"},
    {"name": "UoS Water Bottle 750ml", "price": 17.99, "stock": 55, "category": "Sports"},
    
    # Premium
    {"name": "UoS Gold Trim Premium Mug", "price": 29.99, "stock": 15, "category": "Premium"},
    {"name": "UoS Hand-Painted Mug", "price": 34.99, "stock": 8, "category": "Premium"},
    {"name": "UoS Bone China Mug", "price": 24.99, "stock": 22, "category": "Premium"},
    
    # Kids & Fun
    {"name": "UoS Color-Changing Mug", "price": 13.99, "stock": 48, "category": "Kids"},
    {"name": "UoS Puzzle Mug", "price": 11.99, "stock": 65, "category": "Kids"},
    {"name": "UoS Character Mug", "price": 12.99, "stock": 35, "category": "Kids"},
    
    # Special Edition
    {"name": "UoS 30th Anniversary Mug", "price": 24.99, "stock": 12, "category": "Special"},
    {"name": "UoS Alumni Gold Mug", "price": 27.99, "stock": 18, "category": "Special"},
    {"name": "UoS Graduation Mug", "price": 19.99, "stock": 25, "category": "Special"},
]

CATEGORIES = ["Classic", "Travel", "Sports", "Premium", "Kids", "Special"]

# =============================================================================
# REALISTIC SEASONAL PATTERNS (University Calendar)
# =============================================================================
SEASONAL = {
    1: 0.25,   # January - Exams just ended, low
    2: 0.20,   # February - Winter break
    3: 0.60,   # March - Spring term starts
    4: 0.75,   # April - Mid-term
    5: 0.50,   # May - End of term, exams
    6: 0.30,   # June - Summer starts
    7: 0.25,   # July - Summer
    8: 0.45,   # August - Freshers prep
    9: 2.50,   # September - FRESHERS! HIGHEST
    10: 1.80,  # October - Still high
    11: 1.40,  # November - Pre-Christmas
    12: 1.60,  # December - Christmas gifts
}

# =============================================================================
# SUPPLIERS
# =============================================================================
SUPPLIERS = [
    {"name": "UoS Merchandise Ltd", "email": "orders@uosmerch.co.uk", "lead_time": 7},
    {"name": "Premier Mugs Ltd", "email": "sales@premiermugs.co.uk", "lead_time": 5},
    {"name": "EcoDrink Solutions", "email": "bulk@ecodrink.co.uk", "lead_time": 10},
    {"name": "Suffolk Print Co", "email": "info@suffolkprint.co.uk", "lead_time": 3},
]

# =============================================================================
# USERS
# =============================================================================
USERS = [
    {"username": "admin", "role": "admin", "first": "John", "last": "Smith", "email": "admin@mugnificent.co.uk"},
    {"username": "manager", "role": "manager", "first": "Sarah", "last": "Johnson", "email": "sarah@mugnificent.co.uk"},
    {"username": "warehouse1", "role": "staff", "first": "Mike", "last": "Williams", "email": "mike@mugnificent.co.uk"},
    {"username": "warehouse2", "role": "staff", "first": "Emma", "last": "Brown", "email": "emma@mugnificent.co.uk"},
    {"username": "buyer", "role": "staff", "first": "David", "last": "Jones", "email": "david@mugnificent.co.uk"},
    # Customers
    {"username": "student_alice", "role": "customer", "first": "Alice", "last": "Thompson", "email": "alice@uos.ac.uk"},
    {"username": "student_bob", "role": "customer", "first": "Robert", "last": "Garcia", "email": "bob@uos.ac.uk"},
    {"username": "student_claire", "role": "customer", "first": "Claire", "last": "Martinez", "email": "claire@uos.ac.uk"},
    {"username": "student_dan", "role": "customer", "first": "Daniel", "last": "Anderson", "email": "dan@uos.ac.uk"},
    {"username": "student_emma", "role": "customer", "first": "Emma", "last": "Taylor", "email": "emma.s@uos.ac.uk"},
    # Alumni
    {"username": "alumni_peter", "role": "customer", "first": "Peter", "last": "Wilson", "email": "peter.wilson@alumni.uos.ac.uk"},
    {"username": "alumni_linda", "role": "customer", "first": "Linda", "last": "Moore", "email": "linda.m@alumni.uos.ac.uk"},
    {"username": "alumni_james", "role": "customer", "first": "James", "last": "Jackson", "email": "james.j@alumni.uos.ac.uk"},
]


def generate_phone():
    return f"+44 1473 {random.randint(100, 999)} {random.randint(100, 999)}"


def create_comprehensive_seed():
    """Create comprehensive seed data"""
    print("=" * 70)
    print("MUGNIFICENT COMPREHENSIVE SEED DATA")
    print("=" * 70)
    
    # Create database
    print("\n[1/8] Creating database...")
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # =========================================================================
        # ROLES
        # =========================================================================
        print("[2/8] Creating roles...")
        roles = {}
        for role_name in ["admin", "manager", "staff", "customer"]:
            role = Role(name=role_name, description=f"{role_name.capitalize()} role")
            db.add(role)
            roles[role_name] = role
        db.commit()
        
        # =========================================================================
        # USERS
        # =========================================================================
        print("[3/8] Creating users...")
        user_map = {}
        password = "test1234"  # Same password for all test users
        
        for user_data in USERS:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(password),
                first_name=user_data["first"],
                last_name=user_data["last"],
                role_id=roles[user_data["role"]].id,
                is_staff=user_data["role"] in ["admin", "manager", "staff"],
                is_active=True,
                phone=generate_phone()
            )
            db.add(user)
            user_map[user_data["username"]] = user
        
        db.commit()
        
        # =========================================================================
        # CATEGORIES
        # =========================================================================
        print("[4/8] Creating categories...")
        category_map = {}
        for cat_name in CATEGORIES:
            category = Category(
                name=cat_name,
                slug=cat_name.lower(),
                description=f"UoS {cat_name} merchandise"
            )
            db.add(category)
            db.flush()
            category_map[cat_name] = category
        
        db.commit()
        
        # =========================================================================
        # SUPPLIERS
        # =========================================================================
        print("[5/8] Creating suppliers...")
        supplier_map = {}
        for sup_data in SUPPLIERS:
            supplier = Supplier(
                name=sup_data["name"],
                email=sup_data["email"],
                phone=generate_phone(),
                address=f"{random.randint(1, 100)} High Street, Ipswich, Suffolk",
                lead_time_days=sup_data["lead_time"],
                is_active=True
            )
            db.add(supplier)
            db.flush()
            supplier_map[sup_data["name"]] = supplier
        
        db.commit()
        
        # =========================================================================
        # PRODUCTS
        # =========================================================================
        print("[6/8] Creating products and stock...")
        product_map = {}
        
        for prod_data in PRODUCTS:
            # Select random supplier
            supplier = random.choice(list(supplier_map.values()))
            
            product = Product(
                name=prod_data["name"],
                slug=prod_data["name"].lower().replace(" ", "-"),
                description=f"Official {prod_data['name']} - University of Suffolk licensed merchandise",
                price=Decimal(str(prod_data["price"])),
                category_id=category_map[prod_data["category"]].id,
                stock=prod_data["stock"],
                is_active=True
            )
            db.add(product)
            db.flush()
            
            # Stock item
            unit_cost = prod_data["price"] * Decimal("0.45")  # 45% margin
            stock = StockItem(
                product_id=product.id,
                supplier_id=supplier.id,
                quantity=prod_data["stock"],
                reorder_level=random.randint(10, 25),
                reorder_quantity=random.randint(30, 60),
                unit_cost=unit_cost
            )
            db.add(stock)
            
            # Initial stock movement
            movement = StockMovement(
                stock_item_id=stock.id,
                quantity_change=prod_data["stock"],
                movement_type="in",
                notes="Initial stock"
            )
            db.add(movement)
            
            product_map[prod_data["name"]] = product
        
        db.commit()
        
        # =========================================================================
        # SALES HISTORY (180 days)
        # =========================================================================
        print("[7/8] Creating 180 days of sales history...")
        forecasting = ForecastingService(db)
        
        for product in product_map.values():
            # Base daily sales (varies by product type)
            if "Premium" in product.name or "Special" in product.name:
                base = random.uniform(0.3, 1.5)
            elif "Travel" in product.name or "Sports" in product.name:
                base = random.uniform(1, 3)
            else:
                base = random.uniform(1.5, 4)
            
            # Set seasonal patterns
            for month, multiplier in SEASONAL.items():
                forecasting.set_seasonal_pattern(
                    product_id=product.id,
                    month=month,
                    multiplier=multiplier,
                    notes=f"UoS calendar - {month}"
                )
            
            # Generate 180 days of sales
            for i in range(180):
                date = datetime.utcnow() - timedelta(days=180 - i)
                month = date.month
                
                # Seasonal multiplier
                month_mult = SEASONAL.get(month, 1.0)
                
                # Weekly (weekends slower)
                day_mult = 0.7 if date.weekday() >= 5 else 1.0
                
                # Random variation
                var = random.uniform(0.5, 1.5)
                
                # Calculate quantity
                quantity = int(base * month_mult * day_mult * var)
                quantity = max(0, quantity)
                
                if quantity > 0:
                    revenue = float(product.price) * quantity
                    forecasting.record_sales(product.id, date, quantity, revenue)
        
        db.commit()
        
        # =========================================================================
        # ORDERS (Various States)
        # =========================================================================
        print("[8/8] Creating sample orders...")
        
        # Get some customer users
        customers = [u for u in user_map.values() if u.role_id == roles["customer"].id]
        
        order_statuses = [
            ("completed", 45),  # 45 completed orders
            ("shipped", 15),     # 15 shipped
            ("processing", 8), # 8 processing
            ("pending", 3),     # 3 pending
        ]
        
        for status, count in order_statuses:
            for _ in range(count):
                customer = random.choice(customers)
                created_days_ago = random.randint(1, 60)
                created_at = datetime.utcnow() - timedelta(days=created_days_ago)
                
                # Create order
                num_items = random.randint(1, 4)
                order_items = random.sample(list(product_map.values()), num_items)
                
                subtotal = 0
                for item in order_items:
                    qty = random.randint(1, 3)
                    subtotal += float(item.price) * qty
                
                shipping = 4.99 if subtotal < 50 else 0
                tax = subtotal * 0.20
                total = subtotal + shipping + tax
                
                # Determine dates based on status
                if status == "completed":
                    paid_at = created_at
                    shipped_at = created_at + timedelta(days=random.randint(1, 2))
                    delivered_at = shipped_at + timedelta(days=random.randint(2, 5))
                elif status == "shipped":
                    paid_at = created_at
                    shipped_at = created_at + timedelta(days=random.randint(1, 2))
                    delivered_at = None
                elif status == "processing":
                    paid_at = created_at
                    shipped_at = None
                    delivered_at = None
                else:  # pending
                    paid_at = None
                    shipped_at = None
                    delivered_at = None
                
                order = Order(
                    order_number=f"ORD-{random.randint(10000, 99999)}",
                    user_id=customer.id,
                    subtotal=Decimal(str(subtotal)),
                    shipping_cost=Decimal(str(shipping)),
                    tax=Decimal(str(tax)),
                    total=Decimal(str(total)),
                    status=status,
                    is_paid=paid_at is not None,
                    shipping_address=f"{customer.first_name} {customer.last_name}",
                    shipping_city="Ipswich",
                    shipping_postcode=f"IP{random.randint(1, 10)} {random.randint(1, 9)}AA",
                    created_at=created_at,
                    paid_at=paid_at,
                    shipped_at=shipped_at,
                    delivered_at=delivered_at
                )
                db.add(order)
                db.flush()
                
                # Add items and deduct stock
                for item in order_items:
                    qty = random.randint(1, 3)
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=item.id,
                        product_name=item.name,
                        product_price=item.price,
                        quantity=qty,
                        subtotal=item.price * qty
                    )
                    db.add(order_item)
                    
                    # Deduct stock
                    item.stock = max(0, item.stock - qty)
                
                db.flush()
                
                # Record sales for completed orders
                if status in ["completed", "shipped"]:
                    for item in order_items:
                        qty = random.randint(1, 3)
                        forecasting.record_sales(
                            item.id,
                            created_at,
                            qty,
                            float(item.price) * qty
                        )
        
        db.commit()
        
        # =========================================================================
        # RESTOCK ALERTS (Some products low)
        # =========================================================================
        low_stock_products = random.sample(list(product_map.values()), 5)
        
        for product in low_stock_products:
            alert = RestockAlert(
                product_id=product.id,
                is_active=True,
                is_resolved=False,
                notes=f"Auto-generated: Stock below threshold - {product.stock} remaining"
            )
            db.add(alert)
            
            # Create pending refill request
            stock = db.query(StockItem).filter(StockItem.product_id == product.id).first()
            refill = RefillRequest(
                product_id=product.id,
                supplier_id=stock.supplier_id if stock else None,
                quantity_requested=stock.reorder_quantity if stock else 50,
                status="pending",
                estimated_cost=stock.reorder_quantity * stock.unit_cost if stock else Decimal("100"),
                notes=f"Auto-generated refill request - low stock alert"
            )
            db.add(refill)
        
        db.commit()
        
        # =========================================================================
        # PRINT SUMMARY
        # =========================================================================
        print("\n" + "=" * 70)
        print("✅ SEED DATA CREATED SUCCESSFULLY")
        print("=" * 70)
        
        print(f"\n📊 DATA SUMMARY:")
        print(f"   • Users: {len(user_map)}")
        print(f"   • Products: {len(product_map)}")
        print(f"   • Categories: {len(category_map)}")
        print(f"   • Suppliers: {len(supplier_map)}")
        print(f"   • Orders: {sum(c for _, c in order_statuses)}")
        print(f"   • Sales History: 180 days × {len(product_map)} products")
        
        print(f"\n👤 TEST ACCOUNTS:")
        print(f"   Password for all: {password}")
        print(f"\n   Staff Accounts:")
        print(f"   • admin@mugnificent.co.uk / admin")
        print(f"   • sarah@mugnificent.co.uk / manager")
        print(f"   • mike@mugnificent.co.uk / warehouse1")
        print(f"\n   Customer Accounts:")
        print(f"   • alice@uos.ac.uk / student_alice")
        print(f"   • bob@uos.ac.uk / student_bob")
        
        print(f"\n📈 SEASONAL PATTERNS:")
        print(f"   • September (Freshers): 2.5x")
        print(f"   • October: 1.8x")
        print(f"   • January (Low): 0.25x")
        
        print(f"\n🎯 KEY TESTING SCENARIOS:")
        print(f"   • 5 products have low stock alerts")
        print(f"   • 5 products have pending refill requests")
        print(f"   • Orders in various states (completed, shipped, processing)")
        
        print(f"\n🚀 TO START TESTING:")
        print(f"   1. docker-compose up -d")
        print(f"   2. Visit http://localhost")
        print(f"   3. Login with credentials above")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_comprehensive_seed()
