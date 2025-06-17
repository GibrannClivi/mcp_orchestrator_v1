"""
Pydantic models for the /query endpoint contract.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's natural language question.")
    email: EmailStr = Field(..., description="The user's email address.")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Synthesized answer from Gemma.")
    sources: List[str] = Field(..., description="List of MCP sources used.")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score.")
    cached: bool = Field(..., description="Was the response served from cache?")
    timestamp: str = Field(..., description="ISO8601 timestamp of response.")
    error: Optional[str] = Field(None, description="Error message if any.")
