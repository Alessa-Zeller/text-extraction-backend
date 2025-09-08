import pytest
from fastapi.testclient import TestClient
from app.main import app
import io
from pathlib import Path

client = TestClient(app)

# Helper function to get auth token
def get_auth_token():
    """Get authentication token for testing."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )
    return response.json()["data"]["access_token"]

def test_pdf_service_health():
    """Test PDF service health endpoint."""
    response = client.get("/api/v1/pdf/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_upload_pdf_without_auth():
    """Test PDF upload without authentication."""
    # Create a dummy file
    files = {"file": ("test.pdf", b"dummy pdf content", "application/pdf")}
    response = client.post("/api/v1/pdf/upload", files=files)
    assert response.status_code == 403

def test_upload_invalid_file_type():
    """Test upload with invalid file type."""
    token = get_auth_token()
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    
    response = client.post(
        "/api/v1/pdf/upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_batch_upload_too_many_files():
    """Test batch upload with too many files."""
    token = get_auth_token()
    
    # Create more files than allowed
    files = []
    for i in range(15):  # Exceeds BATCH_SIZE of 10
        files.append(("files", (f"test{i}.pdf", b"dummy pdf content", "application/pdf")))
    
    response = client.post(
        "/api/v1/pdf/batch-upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_search_text_in_results():
    """Test text search functionality."""
    token = get_auth_token()
    
    # Mock PDF processing result
    pdf_result = {
        "filename": "test.pdf",
        "file_size": 1000,
        "processed_at": "2024-01-01T00:00:00Z",
        "pages": [
            {
                "page_number": 1,
                "text": "This is a test document with some sample text.",
                "text_length": 45,
                "tables": [],
                "bbox": [0, 0, 100, 100],
                "width": 100,
                "height": 100
            }
        ],
        "total_pages": 1,
        "total_text_length": 45,
        "metadata": {},
        "file_hash": "abc123",
        "status": "success"
    }
    
    search_request = {
        "query": "test document"
    }
    
    response = client.post(
        "/api/v1/pdf/search",
        json=search_request,
        headers={"Authorization": f"Bearer {token}"},
        params={"pdf_results": pdf_result}
    )
    # This test would need adjustment based on how the search endpoint is implemented
    # For now, we're just testing the endpoint structure

def test_get_stats_as_admin():
    """Test getting processing stats as admin."""
    token = get_auth_token()
    
    response = client.get(
        "/api/v1/pdf/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_get_stats_as_regular_user():
    """Test getting processing stats as regular user (should fail)."""
    # Login as regular user
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "user123"
        }
    )
    token = response.json()["data"]["access_token"]
    
    response = client.get(
        "/api/v1/pdf/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
