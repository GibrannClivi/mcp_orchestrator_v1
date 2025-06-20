"""
Chargebee MCP microservice FastAPI app.
"""
from fastapi import FastAPI, HTTPException
from typing import Optional

from src.mcp_servers.chargebee.service import ChargebeeService
from src.mcp_servers.common.models import ChargebeeCustomer

app = FastAPI(title="Chargebee MCP Service", version="0.1.0")
chargebee_service = ChargebeeService()

@app.get("/lookup", response_model=Optional[ChargebeeCustomer])
async def lookup_customer(email: str):
    """
    Lookup customer details from Chargebee by email.
    """
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    customer_details = await chargebee_service.get_customer_details_by_email(email)
    if not customer_details:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer_details
