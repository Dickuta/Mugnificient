"""
Authentication unit tests.
"""

import pytest
from fastapi import status


class TestHealthCheck:
    """Health check endpoint tests."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "version" in response.json()


class TestRegistration:
    """User registration tests."""

    def test_register_user(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["username"] == "newuser"

    def test_register_duplicate_username(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400


class TestLogin:
    """User login tests."""

    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_password(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "password"}
        )
        assert response.status_code == 401


class TestGetCurrentUser:
    """Get current user tests."""

    def test_get_current_user(self, client, auth_token, test_user):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    def test_unauthorized_access(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_invalid_token(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401
