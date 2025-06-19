import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from mcp_servers.firebase.main import app
from mcp_servers.common.models import MCPRequest

client = TestClient(app)

@pytest.fixture
def test_identifiers():
    """Known identifiers that should exist in the dtwo-qa database."""
    return {
        "email": "test0307@clivi.com.mx",  # Known test user
        "phone": "+526645432356",  # Test user's phone
        "name": "Test",  # Test user's name
    }

@pytest.fixture
def make_request():
    def _make_request(identifier: str, resource: str, params: dict = None):
        return {
            "email": identifier,  # Using email field for any identifier type
            "resource": resource,
            "params": params or {}
        }
    return _make_request

def test_find_user_by_email(test_identifiers, make_request):
    """Test finding a user by their email address."""
    request = make_request(test_identifiers["email"], "users")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None
    assert data["error"] is None
    assert "emailAddress" in data["data"]

def test_find_user_by_phone(test_identifiers, make_request):
    """Test finding a user by their phone number."""
    request = make_request(test_identifiers["phone"], "users")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None
    assert data["error"] is None

def test_find_user_by_name(test_identifiers, make_request):
    """Test finding a user by their name."""
    request = make_request(test_identifiers["name"], "users")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None
    assert data["error"] is None

def test_fetch_appointments(test_identifiers, make_request):
    """Test fetching user appointments."""
    request = make_request(test_identifiers["email"], "appointments")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None
    assert data["error"] is None
    # Appointments should be in the user data
    assert isinstance(data["data"], dict)

def test_fetch_lab_orders(test_identifiers, make_request):
    """Test fetching user lab orders."""
    request = make_request(test_identifiers["email"], "lab_orders")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None
    assert data["error"] is None
    assert "orders" in data["data"]
    assert isinstance(data["data"]["orders"], list)

def test_fetch_tasks(test_identifiers, make_request):
    """Test fetching user tasks."""
    request = make_request(test_identifiers["email"], "tasks")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None
    assert data["error"] is None
    assert "tasks" in data["data"]
    assert isinstance(data["data"]["tasks"], list)

def test_fetch_health_data(test_identifiers, make_request):
    """Test fetching user health data points."""
    request = make_request(test_identifiers["email"], "health_data_points")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None
    assert data["error"] is None
    # Health summary should be in the user data
    assert isinstance(data["data"], dict)

def test_invalid_resource(test_identifiers, make_request):
    """Test requesting an invalid resource type."""
    request = make_request(test_identifiers["email"], "invalid_resource")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == {}
    assert data["error"] is None

def test_nonexistent_user(make_request):
    """Test requesting data for a non-existent user."""
    request = make_request("nonexistent@example.com", "users")
    response = client.post("/mcp/call", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == {}
    assert data["error"] is None

def test_cache_hit(test_identifiers, make_request):
    """Test that responses are properly cached."""
    request = make_request(test_identifiers["email"], "users")
    
    # First call
    response1 = client.post("/mcp/call", json=request)
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Second call should hit cache
    response2 = client.post("/mcp/call", json=request)
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Both responses should be identical
    assert data1 == data2 