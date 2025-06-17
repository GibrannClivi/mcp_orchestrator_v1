"""
Chargebee MCP microservice FastAPI app.
"""
from fastapi import FastAPI
from mcp_servers.common.router import router as mcp_router

app = FastAPI(title="Chargebee MCP Service", version="0.1.0")
app.include_router(mcp_router)
