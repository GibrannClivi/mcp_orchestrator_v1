"""
Router for the /query endpoint.
"""
from fastapi import APIRouter, Request, status
from orchestrator.models.query import QueryRequest, QueryResponse
from orchestrator.services.query_service import handle_query
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: Request, body: QueryRequest):
    try:
        response = await handle_query(body)
        return response
    except Exception as e:
        # Log the error (to be implemented)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=QueryResponse(
                answer="",
                sources=[],
                confidence=0.0,
                cached=False,
                timestamp="",
                error=str(e)
            ).dict()
        )
# TODO: Implement JWT validation for /query in production
