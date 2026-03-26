import pytest


def test_get_predictions_requires_auth(client):
    response = client.get("/api/inventory-ml/predictions")
    assert response.status_code == 401


def test_get_all_predictions(client, admin_token, test_product):
    response = client.get(
        "/api/inventory-ml/predictions",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "product_name" in data[0]
        assert "risk_level" in data[0]


def test_get_product_prediction(client, admin_token, test_product):
    response = client.get(
        f"/api/inventory-ml/predictions/{test_product.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "current_stock" in data
    assert "risk_level" in data
    assert "days_until_stockout" in data


def test_get_predictions_nonexistent_product(client, admin_token):
    response = client.get(
        "/api/inventory-ml/predictions/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404


def test_get_refill_requests(client, admin_token):
    response = client.get(
        "/api/inventory-ml/refill-requests",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_trigger_stock_deduction(client, admin_token, db, test_product):
    from app.models.models import Order, OrderItem
    
    order = Order(
        order_number="TEST-001",
        user_id=1,
        subtotal=9.99,
        shipping_cost=5.00,
        tax=0.80,
        total=15.79,
        is_paid=True
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    order_item = OrderItem(
        order_id=order.id,
        product_id=test_product.id,
        product_name=test_product.name,
        product_price=test_product.price,
        quantity=5,
        subtotal=49.95
    )
    db.add(order_item)
    db.commit()
    
    response = client.post(
        f"/api/inventory-ml/trigger-stock-deduction/{order.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items_updated" in data
    assert len(data["items_updated"]) > 0
