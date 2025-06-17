"""
Business logic for Chargebee MCP microservice.
"""
from mcp_servers.common.models import MCPRequest, MCPResponse
from cachetools import TTLCache
from typing import Any

cache = TTLCache(maxsize=1000, ttl=300)

def get_from_cache(key: str) -> Any:
    return cache.get(key)

def set_in_cache(key: str, value: Any) -> None:
    cache[key] = value

def fetch_chargebee_data(email: str, resource: str, params: dict) -> dict:
    # TODO: Replace with real Chargebee API call
    return {"email": email, "resource": resource, "data": "stubbed chargebee data"}

def handle_mcp_call(body: MCPRequest) -> MCPResponse:
    key = f"{body.email}:{body.resource}:{str(body.params)}"
    cached = get_from_cache(key)
    if cached:
        return MCPResponse(data=cached, error=None)
    data = fetch_chargebee_data(body.email, body.resource, body.params)
    set_in_cache(key, data)
    return MCPResponse(data=data, error=None)
