"""
Integration tests for API endpoints.
Tests that verify frontend-backend integration.
"""

import pytest
from fastapi.testclient import TestClient


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    def test_health_check(self, client):
        """Test API health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test API root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data

    def test_full_customer_journey(self, client, db, test_product):
        """Test complete customer flow: register, login, browse, cart, checkout."""
        # 1. Register
        register_response = client.post("/api/v1/auth/register", json={
            "username": "journeyuser",
            "email": "journey@example.com",
            "password": "testpass123"
        })
        assert register_response.status_code in [200, 201]

        # 2. Login
        login_response = client.post("/api/v1/auth/login", data={
            "username": "journeyuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Browse products
        products_response = client.get("/api/v1/products/", headers=headers)
        assert products_response.status_code == 200

        # 4. Add to cart
        cart_response = client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=2",
            headers=headers
        )
        assert cart_response.status_code in [200, 201]

        # 5. View cart
        cart_view = client.get("/api/v1/cart/", headers=headers)
        assert cart_view.status_code == 200

    def test_forecasting_requires_staff(self, client, test_user):
        """Test that forecasting endpoints require staff access."""
        # Login as regular customer
        login_response = client.post("/api/v1/auth/login", data={
            "username": "testuser",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to access forecasting dashboard
        response = client.get("/api/v1/forecasting/dashboard", headers=headers)
        assert response.status_code in [403, 401]

    def test_forecasting_dashboard_staff(self, client, warehouse_user, warehouse_token):
        """Test that staff can access forecasting dashboard."""
        headers = {"Authorization": f"Bearer {warehouse_token}"}
        response = client.get("/api/v1/forecasting/dashboard", headers=headers)
        assert response.status_code == 200


class TestInventoryIntegration:
    """Integration tests for inventory workflows."""

    def test_inventory_ml_predictions(self, client, warehouse_token):
        """Test inventory ML predictions endpoint."""
        headers = {"Authorization": f"Bearer {warehouse_token}"}
        response = client.get("/api/v1/inventory-ml/predictions", headers=headers)
        assert response.status_code == 200

    def test_inventory_dashboard(self, client, warehouse_token):
        """Test inventory dashboard."""
        headers = {"Authorization": f"Bearer {warehouse_token}"}
        response = client.get("/api/v1/inventory/dashboard", headers=headers)
        assert response.status_code == 200


class TestAdminIntegration:
    """Integration tests for admin functionality."""

    def test_admin_dashboard(self, client, admin_token):
        """Test admin dashboard access."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code == 200

    def test_rbac_permissions(self, client, admin_token):
        """Test RBAC permissions endpoint."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/rbac/permissions", headers=headers)
        assert response.status_code == 200

    def test_rbac_roles(self, client, admin_token):
        """Test RBAC roles endpoint."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/rbac/roles", headers=headers)
        assert response.status_code == 200
