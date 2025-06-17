"""
Chargebee MCP microservice FastAPI app.
"""
from fastapi import FastAPI
from mcp_servers.common.models import MCPRequest, MCPResponse
from .service import handle_mcp_call

app = FastAPI(title="Chargebee MCP Service", version="0.1.0")

@app.post("/mcp/call", response_model=MCPResponse)
async def mcp_call(body: MCPRequest):
    return handle_mcp_call(body)
