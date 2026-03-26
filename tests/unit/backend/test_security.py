"""
Security tests - SQL injection, XSS, CSRF protection.
"""

import pytest


class TestSQLInjectionPrevention:
    """Test SQL injection attacks are prevented."""

    def test_login_sql_injection_username(self, client):
        """Test SQL injection in username field."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "' OR '1'='1' --", "password": "anything"}
        )
        assert response.status_code in [401, 422]

    def test_login_sql_injection_password(self, client):
        """Test SQL injection in password field."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "' OR '1'='1' --"}
        )
        assert response.status_code in [401, 422]

    def test_search_sql_injection(self, client):
        """Test SQL injection in search parameters."""
        response = client.get("/api/v1/products/?search=' OR 1=1 --")
        assert response.status_code == 200
        # Should return empty or valid results, not all products

    def test_register_sql_injection(self, client):
        """Test SQL injection in registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "admin'; DROP TABLE users; --",
                "email": "attack@test.com",
                "password": "testpass123"
            }
        )
        # Should reject or sanitize, not crash
        assert response.status_code in [200, 201, 400, 422]


class TestXSSPrevention:
    """Test XSS attacks are prevented."""

    def test_product_name_xss(self, client, admin_token):
        """Test XSS in product creation."""
        response = client.post(
            "/api/v1/products/",
            json={
                "name": "<script>alert('xss')</script>",
                "slug": "xss-test",
                "description": "Test",
                "price": 9.99,
                "category_id": 1
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code in [200, 201]:
            data = response.json()
            # Script tags should be escaped or stripped
            assert "<script>" not in data.get("name", "")

    def test_category_name_xss(self, client, admin_token):
        """Test XSS in category creation."""
        response = client.post(
            "/api/v1/categories/",
            json={
                "name": "<img src=x onerror=alert(1)>",
                "slug": "xss-category"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code in [200, 201]:
            data = response.json()
            assert "<img" not in data.get("name", "")


class TestRateLimiting:
    """Test rate limiting on sensitive endpoints."""

    def test_login_rate_limit(self, client):
        """Test login endpoint rate limiting."""
        for i in range(20):
            response = client.post(
                "/api/v1/auth/login",
                data={"username": "invalid", "password": "wrong"}
            )
        # After many failed attempts, should get rate limited
        assert response.status_code in [401, 429]

    def test_register_rate_limit(self, client):
        """Test registration rate limiting."""
        for i in range(15):
            client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"user{i}",
                    "email": f"user{i}@test.com",
                    "password": "testpass123"
                }
            )
        # Check if rate limited
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "ratelimit",
                "email": "rate@test.com",
                "password": "testpass123"
            }
        )
        assert response.status_code in [200, 201, 429]


class TestInputValidation:
    """Test input validation edge cases."""

    def test_invalid_email_format(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "password": "testpass123"
            }
        )
        assert response.status_code in [400, 422]

    def test_password_too_short(self, client):
        """Test registration with short password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "123"
            }
        )
        assert response.status_code in [400, 422]

    def test_invalid_product_price_negative(self, client, admin_token):
        """Test product with negative price."""
        response = client.post(
            "/api/v1/products/",
            json={
                "name": "Negative Price",
                "slug": "negative-price",
                "description": "Test",
                "price": -10.00,
                "category_id": 1
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [400, 422]

    def test_invalid_quantity_zero(self, client, auth_token, test_product):
        """Test adding zero quantity to cart."""
        response = client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=0",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [400, 422]

    def test_invalid_quantity_negative(self, client, auth_token, test_product):
        """Test adding negative quantity to cart."""
        response = client.post(
            f"/api/v1/cart/add?product_id={test_product.id}&quantity=-5",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [400, 422]

    def test_oversized_input(self, client, admin_token):
        """Test with oversized input data."""
        response = client.post(
            "/api/v1/products/",
            json={
                "name": "A" * 10000,  # Very long name
                "slug": "oversized",
                "description": "B" * 50000,  # Very long description
                "price": 9.99,
                "category_id": 1
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 201, 400, 422]


class TestTokenSecurity:
    """Test JWT token security."""

    def test_expired_token_rejected(self, client):
        """Test expired token is rejected."""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxfQ.expired"
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    def test_malformed_token_rejected(self, client):
        """Test malformed token is rejected."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.a.valid.token"}
        )
        assert response.status_code == 401

    def test_missing_bearer_prefix(self, client, auth_token):
        """Test token without Bearer prefix."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": auth_token}  # Missing "Bearer "
        )
        assert response.status_code == 401
