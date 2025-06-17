"""
Reusable FastAPI router for /mcp/call endpoint in MCP microservices.
"""
from fastapi import APIRouter, status
from mcp_servers.common.models import MCPRequest, MCPResponse
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/mcp/call", response_model=MCPResponse)
async def mcp_call(body: MCPRequest):
    # TODO: Implement actual business logic in each microservice
    return MCPResponse(data={}, error=None)
