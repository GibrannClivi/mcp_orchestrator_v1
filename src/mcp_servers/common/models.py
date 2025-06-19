"""
Shared Pydantic models for MCP microservices.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict

class MCPRequest(BaseModel):
    email: str = Field(..., description="User identifier (email, name, phone number, etc.)")
    resource: str = Field(..., description="Resource to fetch (users, appointments, etc.)")
    params: Dict = Field(default_factory=dict, description="Additional parameters for filtering")

class MCPResponse(BaseModel):
    data: Any = Field(..., description="Raw data from the MCP service.")
    error: str | None = Field(None, description="Error message, if any.")
