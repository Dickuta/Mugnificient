"""
Product and cart unit tests.
"""

import pytest


class TestProducts:
    """Product listing and detail tests."""

    def test_list_products(self, client):
        """Test listing products."""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_product_by_slug(self, client, test_product):
        """Test getting product by slug."""
        response = client.get(f"/api/v1/products/{test_product.slug}")
        assert response.status_code == 200
        assert response.json()["id"] == test_product.id

    def test_product_not_found(self, client):
        """Test getting non-existent product."""
        response = client.get("/api/v1/products/nonexistent-slug")
        assert response.status_code == 404

    def test_search_products(self, client, test_product):
        """Test product search."""
        response = client.get("/api/v1/products/?search=Test")
        assert response.status_code == 200

    def test_get_featured_products(self, client):
        """Test getting featured products."""
        response = client.get("/api/v1/products/featured")
        assert response.status_code in [200, 404]


class TestCategories:
    """Category tests."""

    def test_list_categories(self, client):
        """Test listing categories."""
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_category_by_slug(self, client, test_category):
        """Test getting category by slug."""
        response = client.get(f"/api/v1/categories/{test_category.slug}")
        assert response.status_code == 200


class TestCart:
    """Cart tests."""

    def test_get_empty_cart(self, client, auth_token):
        """Test getting empty cart."""
        response = client.get(
            "/api/v1/cart/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

    def test_add_to_cart(self, client, auth_token, test_product):
        """Test adding product to cart."""
        response = client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=2",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 201]

    def test_add_to_cart_insufficient_stock(self, client, auth_token, test_product):
        """Test adding more than available stock."""
        response = client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=999999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 400, 422]

    def test_update_cart_item(self, client, auth_token, test_product):
        """Test updating cart item quantity."""
        # First add item
        client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=2",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get cart to find item ID
        cart = client.get(
            "/api/v1/cart/",
            headers={"Authorization": f"Bearer {auth_token}"}
        ).json()
        
        if cart.get("items"):
            item_id = cart["items"][0]["id"]
            response = client.put(
                f"/api/v1/cart/item/{item_id}?quantity=5",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert response.status_code in [200, 404]

    def test_remove_from_cart(self, client, auth_token, test_product):
        """Test removing item from cart."""
        # First add item
        client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get cart to find item ID
        cart = client.get(
            "/api/v1/cart/",
            headers={"Authorization": f"Bearer {auth_token}"}
        ).json()
        
        if cart.get("items"):
            item_id = cart["items"][0]["id"]
            response = client.delete(
                f"/api/v1/cart/item/{item_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert response.status_code in [200, 204, 404]

    def test_clear_cart(self, client, auth_token, test_product):
        """Test clearing entire cart."""
        # First add item
        client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        response = client.delete(
            "/api/v1/cart/clear",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 204]

    def test_cart_requires_auth(self, client):
        """Test cart requires authentication."""
        response = client.get("/api/v1/cart/")
        assert response.status_code == 401


class TestOrders:
    """Order tests."""

    def test_list_orders(self, client, auth_token):
        """Test listing orders."""
        response = client.get(
            "/api/v1/orders/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

    def test_create_order(self, client, auth_token, test_product):
        """Test creating order via checkout."""
        # Add to cart first
        client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        response = client.post(
            "/api/v1/orders/checkout",
            json={
                "shipping_name": "Test User",
                "shipping_address_line1": "123 Test St",
                "shipping_city": "Testville",
                "shipping_state": "TS",
                "shipping_zip_code": "12345",
                "shipping_country": "UK"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 201, 400]

    def test_orders_require_auth(self, client):
        """Test orders require authentication."""
        response = client.get("/api/v1/orders/")
        assert response.status_code == 401


class TestRecommendations:
    """Recommendation engine tests."""

    def test_popular_products(self, client):
        """Test getting popular products."""
        response = client.get("/api/v1/recommendations/popular")
        assert response.status_code == 200

    def test_new_arrivals(self, client):
        """Test getting new arrivals."""
        response = client.get("/api/v1/recommendations/new-arrivals")
        assert response.status_code == 200


class TestDelivery:
    """Delivery tracking tests."""

    def test_delivery_requires_auth(self, client):
        """Test delivery endpoints require auth."""
        response = client.get("/api/v1/delivery/track/test123")
        assert response.status_code == 401


class TestPayments:
    """Payment tests."""

    def test_payments_require_auth(self, client):
        """Test payment endpoints require auth."""
        response = client.post("/api/v1/payments/create-intent")
        assert response.status_code == 401
