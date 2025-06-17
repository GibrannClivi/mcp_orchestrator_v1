"""
Service logic for handling /query requests.
"""
from orchestrator.models.query import QueryRequest, QueryResponse
from orchestrator.config.settings import settings
from orchestrator.cache.in_memory import get_from_cache, set_in_cache
from orchestrator.firestore.firestore_cache import FirestoreCache
from orchestrator.utils.async_tools import run_in_thread
from datetime import datetime
from typing import List, Dict, Any
import hashlib
import httpx
import os

# Stub for Vertex AI integration (to be implemented)
async def analyze_query_with_llm(query: str) -> Dict[str, Any]:
    # TODO: Call Vertex AI with analysis.prompt
    # For now, return a dummy query plan
    return {"sources": ["chargebee", "hubspot"], "plan": "fetch user data from chargebee and hubspot"}

async def synthesize_answer_with_llm(query_plan: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
    # TODO: Call Vertex AI with synthesis.prompt
    # For now, return a dummy answer
    return {"answer": "Synthesized answer based on data.", "sources": list(raw_data.keys()), "confidence": 0.95}

def make_cache_key(query_plan: Dict[str, Any]) -> str:
    # Use a hash of the query plan dict as the cache key
    plan_str = str(query_plan).encode("utf-8")
    return hashlib.sha256(plan_str).hexdigest()

async def call_mcp_service(service: str, email: str, resource: str = "user_data", params: Dict[str, Any] = None) -> Any:
    # TODO: Service discovery/config
    service_ports = {"chargebee": 8081, "hubspot": 8082}
    port = service_ports.get(service)
    if not port:
        return {"error": f"Unknown service: {service}"}
    url = f"http://{service}:{port}/mcp/call"
    payload = {"email": email, "resource": resource, "params": params or {}}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, timeout=10)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

async def handle_query(body: QueryRequest) -> QueryResponse:
    # Step 1: Analyze query with LLM (get query plan)
    query_plan = await analyze_query_with_llm(body.query)
    cache_key = make_cache_key(query_plan)

    # Step 2: Check L2 (in-memory) cache
    cached = get_from_cache(cache_key)
    if cached:
        return QueryResponse(**cached, cached=True, timestamp=datetime.utcnow().isoformat() + "Z")

    # Step 3: Check L1 (Firestore) cache
    firestore_cache = FirestoreCache(settings.FIRESTORE_PROJECT_ID)
    cached = await run_in_thread(firestore_cache.get, cache_key)
    if cached:
        set_in_cache(cache_key, cached)
        return QueryResponse(**cached, cached=True, timestamp=datetime.utcnow().isoformat() + "Z")

    # Step 4: Call MCP microservices as per query plan
    raw_data = {}
    for source in query_plan.get("sources", []):
        raw_data[source] = await call_mcp_service(source, body.email)

    # Step 5: Synthesize answer with LLM
    synthesis = await synthesize_answer_with_llm(query_plan, raw_data)

    # Step 6: Assemble response
    response_dict = {
        "answer": synthesis["answer"],
        "sources": synthesis["sources"],
        "confidence": synthesis["confidence"],
        "cached": False,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "error": None
    }
    # Step 7: Store in both caches
    set_in_cache(cache_key, response_dict)
    await run_in_thread(firestore_cache.set, cache_key, response_dict)

    return QueryResponse(**response_dict)
