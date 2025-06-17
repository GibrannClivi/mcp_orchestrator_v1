"""
Main entrypoint for the MCP Orchestrator FastAPI app.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.routers.query import router as query_router

app = FastAPI(title="MCP Orchestrator", version="0.1.0")

# CORS: Allow all origins for prototype (lock down in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ALLOW_ORIGINS", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(query_router)

# TODO: Implement JWT validation for /query in production
