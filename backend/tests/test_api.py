"""
Integration tests for the API endpoints.
Run: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_returns_200(self):
        """Test that the health endpoint returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_login_success(self):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={"email": "manager@company.com", "password": "manager123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "user" in response.json()
    
    def test_login_failure(self):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/auth/login",
            json={"email": "wrong@company.com", "password": "wrong123"}
        )
        assert response.status_code == 401


class TestProductsEndpoint:
    """Test products API endpoints."""
    
    def test_list_products(self):
        """Test listing products."""
        response = client.get("/api/products")
        assert response.status_code == 200
        assert "data" in response.json()
        assert "pagination" in response.json()


class TestSupportEndpoints:
    """Test support API endpoints."""
    
    def test_analyze_endpoint(self):
        """Test the analyze endpoint."""
        response = client.post(
            "/api/support/analyze",
            json={"message": "My laptop is broken"}
        )
        assert response.status_code == 200
        assert "intent" in response.json()
        assert "sentiment" in response.json()
        assert "response" in response.json()