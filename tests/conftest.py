"""
Shared test fixtures for Mugnificent test suite.

This conftest.py provides fixtures for:
- Database sessions (SQLite for unit tests)
- Test client
- Test users and authentication tokens
- Test products and categories
"""

import pytest
import uuid
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

from app.main import app
from app.core.data.database import Base, get_db
from app.core.security.security import get_password_hash
from app.models.models import User, Role, Permission, Product, Category, StockItem


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    db_name = f"test_{uuid.uuid4().hex}.db"
    engine = create_engine(
        f"sqlite:///{db_name}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    db_session = TestingSessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    engine.dispose()
    try:
        os.unlink(db_name)
    except:
        pass


@pytest.fixture(scope="function")
def client():
    """Create a test client with fresh database."""
    db_name = f"test_{uuid.uuid4().hex}.db"
    engine = create_engine(
        f"sqlite:///{db_name}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    engine.dispose()
    try:
        os.unlink(db_name)
    except:
        pass


@pytest.fixture
def test_user(db):
    """Create a test customer user."""
    role = db.query(Role).filter(Role.name == "customer").first()
    if not role:
        role = Role(name="customer", description="Customer")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        role_id=role.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create a test admin user."""
    role = db.query(Role).filter(Role.name == "admin").first()
    if not role:
        role = Role(name="admin", description="Admin")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("adminpass123"),
        role_id=role.id,
        is_staff=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def warehouse_user(db):
    """Create a test warehouse staff user."""
    role = db.query(Role).filter(Role.name == "warehouse").first()
    if not role:
        role = Role(name="warehouse", description="Warehouse Staff")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    user = User(
        username="warehouse",
        email="warehouse@example.com",
        password_hash=get_password_hash("warehouse123"),
        role_id=role.id,
        is_staff=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_category(db):
    """Create a test category."""
    category = Category(name="Mugs", slug="mugs", description="Coffee and tea mugs")
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def test_product(db, test_category):
    """Create a test product with stock."""
    product = Product(
        name="Test Mug",
        slug="test-mug",
        description="A test mug",
        price=9.99,
        category_id=test_category.id,
        stock=50,
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    stock = StockItem(
        product_id=product.id,
        quantity=50,
        reorder_level=10,
        reorder_quantity=30
    )
    db.add(stock)
    db.commit()
    
    return product


@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    """Get authentication token for admin user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "adminpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def warehouse_token(client, warehouse_user):
    """Get authentication token for warehouse staff."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "warehouse", "password": "warehouse123"}
    )
    return response.json()["access_token"]
