"""
Forecasting unit tests.
"""

import pytest


class TestForecastingDashboard:
    """Forecasting dashboard tests."""

    def test_forecasting_dashboard_requires_auth(self, client):
        """Test that forecasting dashboard requires authentication."""
        response = client.get("/api/v1/forecasting/dashboard")
        assert response.status_code == 401

    def test_forecasting_dashboard_requires_staff(self, client, auth_token):
        """Test that forecasting dashboard requires staff access."""
        response = client.get(
            "/api/v1/forecasting/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 403

    def test_forecasting_dashboard_staff_access(self, client, warehouse_token):
        """Test staff can access forecasting dashboard."""
        response = client.get(
            "/api/v1/forecasting/dashboard",
            headers={"Authorization": f"Bearer {warehouse_token}"}
        )
        assert response.status_code == 200


class TestForecastingPredictions:
    """Forecast prediction tests."""

    def test_get_forecast(self, client, warehouse_token, test_product):
        """Test getting forecast for a product."""
        response = client.get(
            f"/api/v1/forecasting/products/{test_product.id}/forecast",
            headers={"Authorization": f"Bearer {warehouse_token}"}
        )
        assert response.status_code in [200, 404]

    def test_get_seasonal_patterns(self, client, warehouse_token, test_product):
        """Test getting seasonal patterns for a product."""
        response = client.get(
            f"/api/v1/forecasting/products/{test_product.id}/seasonal-patterns",
            headers={"Authorization": f"Bearer {warehouse_token}"}
        )
        assert response.status_code in [200, 404]


class TestAutoOrder:
    """Auto-order tests."""

    def test_auto_order_settings(self, client, warehouse_token, test_product):
        """Test getting auto-order settings."""
        response = client.get(
            f"/api/v1/forecasting/auto-order/settings/{test_product.id}",
            headers={"Authorization": f"Bearer {warehouse_token}"}
        )
        assert response.status_code in [200, 404]

    def test_update_auto_order_settings(self, client, warehouse_token, test_product):
        """Test updating auto-order settings."""
        response = client.put(
            f"/api/v1/forecasting/auto-order/settings/{test_product.id}",
            json={
                "enabled": True,
                "min_stock_threshold": 10,
                "order_quantity": 50
            },
            headers={"Authorization": f"Bearer {warehouse_token}"}
        )
        assert response.status_code in [200, 404]

    def test_purchase_orders_list(self, client, warehouse_token):
        """Test listing purchase orders."""
        response = client.get(
            "/api/v1/forecasting/purchase-orders",
            headers={"Authorization": f"Bearer {warehouse_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestInventoryML:
    """Inventory ML tests."""

    def test_inventory_predictions(self, client, warehouse_token):
        """Test getting inventory predictions."""
        response = client.get(
            "/api/v1/inventory-ml/predictions",
            headers={"Authorization": f"Bearer {warehouse_token}"}
        )
        assert response.status_code == 200

    def test_refill_requests(self, client, warehouse_token):
        """Test listing refill requests."""
        response = client.get(
            "/api/v1/inventory-ml/refill-requests",
            headers={"Authorization": f"Bearer {warehouse_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAdmin:
    """Admin functionality tests."""

    def test_admin_dashboard(self, client, admin_token):
        """Test admin dashboard access."""
        response = client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_rbac_permissions(self, client, admin_token):
        """Test RBAC permissions."""
        response = client.get(
            "/api/v1/rbac/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_rbac_roles(self, client, admin_token):
        """Test RBAC roles."""
        response = client.get(
            "/api/v1/rbac/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
