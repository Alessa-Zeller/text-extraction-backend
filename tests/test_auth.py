import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]

def test_login_user():
    """Test user login with existing credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]

def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_get_profile_without_token():
    """Test accessing profile without authentication."""
    response = client.get("/api/v1/auth/profile")
    assert response.status_code == 403  # No Authorization header

def test_get_profile_with_token():
    """Test accessing profile with valid token."""
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )
    token = login_response.json()["data"]["access_token"]
    
    # Access profile with token
    response = client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "admin@example.com"
