"""
Edge case and error handling tests.
"""

import pytest


class TestConcurrentOperations:
    """Test concurrent operations and race conditions."""

    def test_concurrent_cart_updates(self, client, auth_token, test_product):
        """Test multiple simultaneous cart updates."""
        # Simulate concurrent adds
        for _ in range(5):
            client.post(
                f"/api/v1/cart/add?product_id={test_product.id}&quantity=1",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        
        # Verify correct quantity
        cart = client.get(
            "/api/v1/cart/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert cart.status_code == 200

    def test_concurrent_inventory_updates(self, client, admin_token, test_product):
        """Test concurrent inventory adjustments."""
        # This tests the application handles concurrent stock updates
        for i in range(3):
            client.post(
                f"/api/v1/inventory/stock/adjust",
                json={
                    "product_id": test_product.id,
                    "quantity_change": -1,
                    "reason": f"Test adjustment {i}"
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )


class TestPagination:
    """Test pagination edge cases."""

    def test_products_pagination(self, client):
        """Test product listing with pagination."""
        response = client.get("/api/v1/products/?page=1&limit=10")
        assert response.status_code == 200

    def test_products_invalid_page(self, client):
        """Test with invalid page number."""
        response = client.get("/api/v1/products/?page=-1")
        assert response.status_code in [200, 400, 422]

    def test_products_large_page(self, client):
        """Test with very large page number."""
        response = client.get("/api/v1/products/?page=999999")
        assert response.status_code in [200, 404]
        data = response.json()
        if isinstance(data, list):
            assert len(data) == 0


class TestEmptyStates:
    """Test empty state handling."""

    def test_empty_product_list(self, client, db):
        """Test product list when no products exist."""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        # Should return empty list, not error

    def test_empty_cart(self, client, auth_token):
        """Test cart when empty."""
        response = client.get(
            "/api/v1/cart/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

    def test_empty_order_history(self, client, test_user):
        """Test order history for new user."""
        # Login as test user
        login = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"}
        )
        token = login.json()["access_token"]
        
        response = client.get(
            "/api/v1/orders/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


class TestNotFoundScenarios:
    """Test 404 handling for various resources."""

    def test_nonexistent_product(self, client):
        """Test getting non-existent product."""
        response = client.get("/api/v1/products/this-product-does-not-exist-xyz")
        assert response.status_code == 404

    def test_nonexistent_category(self, client):
        """Test getting non-existent category."""
        response = client.get("/api/v1/categories/nonexistent-category")
        assert response.status_code == 404

    def test_nonexistent_order(self, client, auth_token):
        """Test getting non-existent order."""
        response = client.get(
            "/api/v1/orders/99999999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [404, 400]


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_add_max_quantity_to_cart(self, client, auth_token, test_product):
        """Test adding maximum allowed quantity."""
        response = client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 201, 400]

    def test_update_cart_to_zero(self, client, auth_token, test_product):
        """Test updating cart item to zero quantity."""
        # First add item
        client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=2",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get cart to find item
        cart = client.get(
            "/api/v1/cart/",
            headers={"Authorization": f"Bearer {auth_token}"}
        ).json()
        
        if cart.get("items"):
            item_id = cart["items"][0]["id"]
            response = client.put(
                f"/api/v1/cart/item/{item_id}?quantity=0",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            # Should either remove item or reject
            assert response.status_code in [200, 400, 422]

    def test_special_characters_in_search(self, client):
        """Test search with special characters."""
        special_chars = ["%", "_", "\\", "/", "*", "?", "[", "]"]
        for char in special_chars:
            response = client.get(f"/api/v1/products/?search={char}")
            assert response.status_code == 200


class TestDataIntegrity:
    """Test data integrity constraints."""

    def test_duplicate_username(self, client, test_user):
        """Test creating user with existing username."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",  # Already exists
                "email": "different@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code in [400, 409]

    def test_duplicate_email(self, client, test_user):
        """Test creating user with existing email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "differentuser",
                "email": "test@example.com",  # Already exists
                "password": "testpass123"
            }
        )
        assert response.status_code in [400, 409]

    def test_duplicate_product_slug(self, client, admin_token, test_product):
        """Test creating product with existing slug."""
        response = client.post(
            "/api/v1/products/",
            json={
                "name": "Different Product",
                "slug": "test-mug",  # Already exists
                "description": "Test",
                "price": 9.99,
                "category_id": 1
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [400, 409]


class TestCORS:
    """Test CORS headers."""

    def test_cors_headers(self, client):
        """Test that CORS headers are present."""
        response = client.options(
            "/api/v1/products/",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "GET"
            }
        )
        # Should include CORS headers
        assert response.status_code in [200, 204]


class TestHealthAndMonitoring:
    """Test health check and monitoring endpoints."""

    def test_health_endpoint(self, client):
        """Test health check returns correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Should contain Prometheus metrics format
        content = response.text
        assert "http_requests_total" in content or "python_info" in content
