import pytest
from fastapi.testclient import TestClient
from mcp_servers.firebase.main import app
from mcp_servers.common.models import MCPRequest

client = TestClient(app)

@pytest.fixture
def valid_request():
    return {
        "email": "test@example.com",
        "resource": "users",
        "params": {"foo": "bar"}
    }

def test_mcp_call_cache_miss(valid_request):
    # First call should be a cache miss and return stubbed data
    response = client.post("/mcp/call", json=valid_request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == valid_request["email"]
    assert data["data"]["resource"] == valid_request["resource"]
    assert data["data"]["data"] == "stubbed firebase data"
    assert data["error"] is None

def test_mcp_call_cache_hit(valid_request):
    # First call to populate cache
    client.post("/mcp/call", json=valid_request)
    # Second call should hit the cache
    response = client.post("/mcp/call", json=valid_request)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == valid_request["email"]
    assert data["data"]["resource"] == valid_request["resource"]
    assert data["data"]["data"] == "stubbed firebase data"
    assert data["error"] is None

def test_mcp_call_invalid_email():
    # Should fail validation for invalid email
    bad_request = {
        "email": "not-an-email",
        "resource": "users",
        "params": {}
    }
    response = client.post("/mcp/call", json=bad_request)
    assert response.status_code == 422 