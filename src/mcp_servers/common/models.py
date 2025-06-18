"""
Shared Pydantic models for MCP microservices.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict

class MCPRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address.")
    resource: str = Field(..., description="Resource to fetch (e.g., 'subscriptions').")
    params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters.")

class MCPResponse(BaseModel):
    data: Any = Field(..., description="Raw data from the MCP service.")
    error: str | None = Field(None, description="Error message, if any.")
