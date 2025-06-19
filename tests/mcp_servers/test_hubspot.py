import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from mcp_servers.hubspot.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def set_env():
    os.environ["HUBSPOT_API_KEY"] = os.environ.get("HUBSPOT_API_KEY", "test-api-key")

@patch("mcp_servers.hubspot.service.find_contact_by_email", new_callable=AsyncMock)
def test_contacts(mock_find_contact):
    mock_find_contact.return_value = {"id": "123", "email": "user@example.com"}
    response = client.post("/mcp/call", json={
        "email": "user@example.com",
        "resource": "contacts",
        "params": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "user@example.com"
    assert data["error"] is None

@patch("mcp_servers.hubspot.service.find_contact_by_email", new_callable=AsyncMock)
@patch("mcp_servers.hubspot.service.get_contact_deals", new_callable=AsyncMock)
def test_deals(mock_get_deals, mock_find_contact):
    mock_find_contact.return_value = {"id": "123", "email": "user@example.com"}
    mock_get_deals.return_value = [{"dealname": "Test Deal"}]
    response = client.post("/mcp/call", json={
        "email": "user@example.com",
        "resource": "deals",
        "params": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert "deals" in data["data"]
    assert data["data"]["deals"][0]["dealname"] == "Test Deal"
    assert data["error"] is None

@patch("mcp_servers.hubspot.service.find_contact_by_email", new_callable=AsyncMock)
@patch("mcp_servers.hubspot.service.get_contact_conversations", new_callable=AsyncMock)
def test_conversations(mock_get_conversations, mock_find_contact):
    mock_find_contact.return_value = {"id": "123", "email": "user@example.com"}
    mock_get_conversations.return_value = [{"thread": "Test Conversation"}]
    response = client.post("/mcp/call", json={
        "email": "user@example.com",
        "resource": "conversations",
        "params": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data["data"]
    assert data["data"]["conversations"][0]["thread"] == "Test Conversation"
    assert data["error"] is None

@patch("mcp_servers.hubspot.service.find_contact_by_email", new_callable=AsyncMock)
@patch("mcp_servers.hubspot.service.get_contact_tickets", new_callable=AsyncMock)
def test_tickets(mock_get_tickets, mock_find_contact):
    mock_find_contact.return_value = {"id": "123", "email": "user@example.com"}
    mock_get_tickets.return_value = [{"subject": "Test Ticket"}]
    response = client.post("/mcp/call", json={
        "email": "user@example.com",
        "resource": "tickets",
        "params": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert "tickets" in data["data"]
    assert data["data"]["tickets"][0]["subject"] == "Test Ticket"
    assert data["error"] is None

@patch("mcp_servers.hubspot.service.find_contact_by_email", new_callable=AsyncMock)
def test_contact_not_found(mock_find_contact):
    mock_find_contact.return_value = {}
    response = client.post("/mcp/call", json={
        "email": "notfound@example.com",
        "resource": "deals",
        "params": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["error"] == "Contact not found"

@pytest.mark.skipif(os.environ.get("RUN_HUBSPOT_LIVE_TESTS") != "1", reason="Live HubSpot test skipped unless RUN_HUBSPOT_LIVE_TESTS=1")
def test_live_contact_kyle():
    """
    Live test against HubSpot API for contact kyle@kjernigan.net.
    Requires HUBSPOT_API_KEY and the contact to exist in your HubSpot account.
    """
    response = client.post("/mcp/call", json={
        "email": "kyle@kjernigan.net",
        "resource": "contacts",
        "params": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data"].get("email") == "kyle@kjernigan.net" or data["data"] != {}, f"Response: {data}"
    assert data["error"] is None 