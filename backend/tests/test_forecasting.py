import pytest
from datetime import datetime


def test_get_forecast_requires_auth(client):
    response = client.get("/api/forecasting/products/1/forecast")
    assert response.status_code == 401


def test_get_forecast_unauthorized(client, admin_token, test_product):
    response = client.get(
        f"/api/forecasting/products/{test_product.id}/forecast",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_forecast_returns_data(client, admin_token, test_product):
    response = client.get(
        f"/api/forecasting/products/{test_product.id}/forecast",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "current_stock" in data
    assert "avg_daily_sales" in data
    assert "forecasts" in data


def test_seasonal_patterns(client, admin_token, test_product):
    response = client.post(
        f"/api/forecasting/products/{test_product.id}/seasonal-patterns",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "month": 9,
            "demand_multiplier": 1.5,
            "notes": "University intake season"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == 9
    assert data["demand_multiplier"] == 1.5


def test_seasonal_patterns_invalid_month(client, admin_token, test_product):
    response = client.post(
        f"/api/forecasting/products/{test_product.id}/seasonal-patterns",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "month": 13,
            "demand_multiplier": 1.5
        }
    )
    assert response.status_code == 400


def test_get_dashboard(client, admin_token):
    response = client.get(
        "/api/forecasting/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total_products" in data


def test_auto_order_settings(client, admin_token, test_product):
    response = client.get(
        f"/api/forecasting/auto-order/settings/{test_product.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "enabled" in data
    assert data["enabled"] == False


def test_update_auto_order_settings(client, admin_token, test_product):
    response = client.put(
        f"/api/forecasting/auto-order/settings/{test_product.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "enabled": True,
            "min_stock_threshold": 15,
            "order_quantity": 50
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] == True
    assert data["min_stock_threshold"] == 15
