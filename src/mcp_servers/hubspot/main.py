"""
HubSpot MCP microservice FastAPI app.
"""
from fastapi import FastAPI
from mcp_servers.common.models import MCPRequest, MCPResponse
from .service import handle_mcp_call

app = FastAPI(title="HubSpot MCP Service", version="0.1.0")

@app.post("/mcp/call", response_model=MCPResponse)
async def mcp_call(body: MCPRequest) -> MCPResponse:
    """
    Handle MCP calls to HubSpot API.
    
    Supported resources:
    - contacts: Get contact information
    - deals: Get deals associated with a contact
    - conversations: Get conversations for a contact
    - tickets: Get tickets associated with a contact
    """
    return await handle_mcp_call(body)
