import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.models import User, Role, Permission, Product, Category, StockItem


@pytest.fixture(scope="function")
def db():
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
    import os
    try:
        os.unlink(db_name)
    except:
        pass


@pytest.fixture(scope="function")
def client():
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
    import os
    try:
        os.unlink(db_name)
    except:
        pass


@pytest.fixture
def test_user(db):
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
def test_category(db):
    category = Category(name="Mugs", slug="mugs", description="Coffee and tea mugs")
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def test_product(db, test_category):
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
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "adminpass123"}
    )
    return response.json()["access_token"]
