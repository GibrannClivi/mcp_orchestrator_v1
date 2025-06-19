"""
Business logic for Firebase MCP microservice.
"""
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from mcp_servers.common.models import MCPRequest, MCPResponse
from cachetools import TTLCache

# Initialize Firebase app only once
if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_CREDENTIALS")
    if not cred_path:
        raise RuntimeError("FIREBASE_CREDENTIALS environment variable not set.")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

cache = TTLCache(maxsize=1000, ttl=300)

def get_from_cache(key: str) -> Any:
    return cache.get(key)

def set_in_cache(key: str, value: Any) -> None:
    cache[key] = value

def to_serializable(data: Any) -> Any:
    """Convert Firestore data types to JSON-serializable format."""
    if isinstance(data, dict):
        return {k: to_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [to_serializable(item) for item in data]
    elif isinstance(data, (firestore.DocumentReference, firestore.CollectionReference)):
        return str(data.path)
    elif hasattr(data, 'timestamp'):  # For Firestore timestamps
        try:
            return data.timestamp().isoformat()
        except (ValueError, AttributeError):
            return str(data)
    elif isinstance(data, (int, float)):
        # Try to convert to timestamp if it looks like one (between 2020 and 2030)
        try:
            if 1577836800 <= float(data) <= 1893456000:  # 2020-01-01 to 2030-01-01
                return datetime.fromtimestamp(data).isoformat()
        except (ValueError, OSError, TypeError):
            pass
        return data
    return data

def find_user(identifier: str) -> Dict:
    """
    Find a user by email, name, or ID.
    
    Args:
        identifier: Can be email, name, or ID (phone number, numeric ID, etc.)
    """
    users_ref = db.collection("users")
    
    # Try direct document ID first (could be phone number or Firebase ID)
    doc = users_ref.document(identifier).get()
    if doc.exists:
        return to_serializable(doc.to_dict())
    
    # Try email field
    docs = users_ref.where(filter=firestore.FieldFilter("emailAddress", "==", identifier)).get()
    if docs:
        return to_serializable(docs[0].to_dict())
    
    # Try name fields (first name or display name)
    docs = users_ref.where(filter=firestore.FieldFilter("nameDisplay", "==", identifier)).get()
    if not docs:
        docs = users_ref.where(filter=firestore.FieldFilter("nameFirst", "==", identifier)).get()
    if docs:
        return to_serializable(docs[0].to_dict())
    
    # Try phone number variations
    if identifier.startswith("+"):
        identifier = identifier[1:]  # Remove leading +
    variations = [
        identifier,
        f"+{identifier}",
        identifier.lstrip("0"),  # Remove leading zeros
    ]
    for var in variations:
        doc = users_ref.document(var).get()
        if doc.exists:
            return to_serializable(doc.to_dict())
        docs = users_ref.where(filter=firestore.FieldFilter("whatsapp", "==", var)).get()
        if docs:
            return to_serializable(docs[0].to_dict())
    
    return {}

def fetch_firebase_data(identifier: str, resource: str, params: dict) -> dict:
    """
    Fetch data from Firebase based on resource type.
    
    Args:
        identifier: User identifier (email, name, or ID)
        resource: Type of data to fetch (users, appointments, etc.)
        params: Additional parameters for filtering
    """
    if resource == "users":
        return find_user(identifier)
    
    # For other resources, we need the user's ID first
    user_data = find_user(identifier)
    if not user_data:
        return {}
    
    user_id = user_data.get("id")
    if not user_id:
        return {}
    
    if resource == "appointments":
        return to_serializable(user_data.get("appointments", {}))
    elif resource == "lab_orders":
        # Assuming lab orders are stored in a subcollection
        orders_ref = db.collection("users").document(user_id).collection("lab_orders")
        orders = [doc.to_dict() for doc in orders_ref.get()]
        return {"orders": to_serializable(orders)}
    elif resource == "tasks":
        # Assuming tasks are stored in a subcollection
        tasks_ref = db.collection("users").document(user_id).collection("tasks")
        tasks = [doc.to_dict() for doc in tasks_ref.get()]
        return {"tasks": to_serializable(tasks)}
    elif resource == "health_data_points":
        return to_serializable(user_data.get("healthSummary", {}))
    else:
        return {}

def handle_mcp_call(body: MCPRequest) -> MCPResponse:
    """Handle MCP request by fetching appropriate Firebase data."""
    key = f"{body.email}:{body.resource}:{str(body.params)}"
    cached = get_from_cache(key)
    if cached:
        return MCPResponse(data=cached, error=None)
    
    try:
        data = fetch_firebase_data(body.email, body.resource, body.params)
        set_in_cache(key, data)
        return MCPResponse(data=data, error=None)
    except Exception as e:
        return MCPResponse(data={}, error=str(e)) 