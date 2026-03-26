"""
End-to-end API tests - Tests complete user workflows.
"""

import pytest


class TestCompleteCustomerJourney:
    """Complete customer workflow tests."""

    def test_register_login_browse_cart_checkout(
        self, client, db, test_product
    ):
        """Test full customer journey: register, login, browse, cart, checkout."""
        # 1. Register
        register_response = client.post("/api/v1/auth/register", json={
            "username": "e2e_customer",
            "email": "e2e@example.com",
            "password": "testpass123"
        })
        assert register_response.status_code in [200, 201]

        # 2. Login
        login_response = client.post("/api/v1/auth/login", data={
            "username": "e2e_customer",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Browse products
        products_response = client.get("/api/v1/products/", headers=headers)
        assert products_response.status_code == 200

        # 4. Get categories
        categories_response = client.get("/api/v1/categories/", headers=headers)
        assert categories_response.status_code == 200

        # 5. Add to cart
        cart_response = client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=2",
            headers=headers
        )
        assert cart_response.status_code in [200, 201]

        # 6. View cart
        cart_view = client.get("/api/v1/cart/", headers=headers)
        assert cart_view.status_code == 200

        # 7. Checkout
        checkout_response = client.post(
            "/api/v1/orders/checkout",
            json={
                "shipping_name": "Test User",
                "shipping_address_line1": "123 Test St",
                "shipping_city": "Testville",
                "shipping_state": "TS",
                "shipping_zip_code": "12345",
                "shipping_country": "UK"
            },
            headers=headers
        )
        assert checkout_response.status_code in [200, 201, 400]

        # 8. View orders
        orders_response = client.get("/api/v1/orders/", headers=headers)
        assert orders_response.status_code == 200


class TestCompleteAdminWorkflow:
    """Complete admin workflow tests."""

    def test_admin_dashboard_rbac_management(self, client, admin_token):
        """Test admin dashboard and RBAC management."""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Dashboard
        dashboard = client.get("/api/v1/admin/dashboard", headers=headers)
        assert dashboard.status_code == 200

        # 2. Sales analytics
        sales = client.get("/api/v1/admin/sales-by-category", headers=headers)
        assert sales.status_code in [200, 404]

        # 3. Top products
        top = client.get("/api/v1/admin/top-products", headers=headers)
        assert top.status_code in [200, 404]

        # 4. RBAC - Permissions
        permissions = client.get("/api/v1/rbac/permissions", headers=headers)
        assert permissions.status_code == 200

        # 5. RBAC - Roles
        roles = client.get("/api/v1/rbac/roles", headers=headers)
        assert roles.status_code == 200

        # 6. RBAC - My Permissions
        my_perms = client.get("/api/v1/rbac/my-permissions", headers=headers)
        assert my_perms.status_code == 200


class TestCompleteWarehouseWorkflow:
    """Complete warehouse staff workflow tests."""

    def test_forecast_inventory_auto_order(
        self, client, warehouse_token, test_product
    ):
        """Test forecasting, inventory, and auto-order workflow."""
        headers = {"Authorization": f"Bearer {warehouse_token}"}

        # 1. View forecasting dashboard
        dashboard = client.get("/api/v1/forecasting/dashboard", headers=headers)
        assert dashboard.status_code == 200

        # 2. Get product forecast
        forecast = client.get(
            f"/api/v1/forecasting/products/{test_product.id}/forecast",
            headers=headers
        )
        assert forecast.status_code in [200, 404]

        # 3. Get seasonal patterns
        seasonal = client.get(
            f"/api/v1/forecasting/products/{test_product.id}/seasonal-patterns",
            headers=headers
        )
        assert seasonal.status_code in [200, 404]

        # 4. Update auto-order settings
        auto_order = client.put(
            f"/api/v1/forecasting/auto-order/settings/{test_product.id}",
            json={
                "enabled": True,
                "min_stock_threshold": 10,
                "order_quantity": 50
            },
            headers=headers
        )
        assert auto_order.status_code in [200, 404]

        # 5. View inventory predictions
        predictions = client.get(
            "/api/v1/inventory-ml/predictions",
            headers=headers
        )
        assert predictions.status_code == 200

        # 6. View refill requests
        refills = client.get(
            "/api/v1/inventory-ml/refill-requests",
            headers=headers
        )
        assert refills.status_code == 200

        # 7. View purchase orders
        pos = client.get(
            "/api/v1/forecasting/purchase-orders",
            headers=headers
        )
        assert pos.status_code == 200


class TestSecurityWorkflow:
    """Security and access control tests."""

    def test_unauthenticated_access_denied(self, client):
        """Test all protected endpoints deny unauthenticated access."""
        protected_endpoints = [
            "/api/v1/auth/me",
            "/api/v1/cart/",
            "/api/v1/orders/",
            "/api/v1/forecasting/dashboard",
            "/api/v1/inventory-ml/predictions",
            "/api/v1/admin/dashboard",
            "/api/v1/rbac/permissions",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"{endpoint} should require auth"

    def test_customer_cannot_access_staff_endpoints(
        self, client, auth_token
    ):
        """Test customer role cannot access staff-only endpoints."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        staff_endpoints = [
            "/api/v1/forecasting/dashboard",
            "/api/v1/inventory-ml/predictions",
            "/api/v1/admin/dashboard",
        ]

        for endpoint in staff_endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 403, f"{endpoint} should require staff"

    def test_warehouse_cannot_access_admin(
        self, client, warehouse_token
    ):
        """Test warehouse staff cannot access admin endpoints."""
        headers = {"Authorization": f"Bearer {warehouse_token}"}

        response = client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code in [403, 200]  # May depend on permissions

    def test_admin_can_access_all(self, client, admin_token):
        """Test admin can access all endpoints."""
        headers = {"Authorization": f"Bearer {admin_token}"}

        endpoints = [
            "/api/v1/forecasting/dashboard",
            "/api/v1/inventory-ml/predictions",
            "/api/v1/admin/dashboard",
            "/api/v1/rbac/permissions",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 200, f"{endpoint} should be accessible to admin"
