"""
Business logic for HubSpot MCP microservice.
"""
import os
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from cachetools import TTLCache
import hubspot
from hubspot.crm.contacts import ApiException as ContactsApiException
from hubspot.crm.deals import ApiException as DealsApiException
from hubspot.conversations.visitor_identification import ApiException as ConversationsApiException
from mcp_servers.common.models import MCPRequest, MCPResponse

# Initialize HubSpot client
if not os.getenv("HUBSPOT_API_KEY"):
    raise RuntimeError("HUBSPOT_API_KEY environment variable not set.")

client = hubspot.Client.create(access_token=os.getenv("HUBSPOT_API_KEY"))
cache = TTLCache(maxsize=1000, ttl=300)

def get_from_cache(key: str) -> Any:
    return cache.get(key)

def set_in_cache(key: str, value: Any) -> None:
    cache[key] = value

async def find_contact_by_email(email: str) -> Dict:
    """Find a HubSpot contact by email address."""
    try:
        filter_groups = [
            {
                "filters": [
                    {
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }
                ]
            }
        ]
        
        result = await asyncio.to_thread(
            client.crm.contacts.search_api.do_search,
            {"filterGroups": filter_groups}
        )
        
        if result.results:
            return result.results[0].to_dict()
        return {}
    except ContactsApiException as e:
        return {"error": f"HubSpot Contacts API error: {str(e)}"}

async def get_contact_deals(contact_id: str) -> List[Dict]:
    """Get all deals associated with a contact."""
    try:
        result = await asyncio.to_thread(
            client.crm.deals.basic_api.get_all,
            associations=["contacts"],
            properties=["dealname", "amount", "dealstage", "closedate"]
        )
        
        # Filter deals for this contact
        contact_deals = [
            deal.to_dict() for deal in result.results 
            if any(assoc.id == contact_id for assoc in deal.associations.get("contacts", []))
        ]
        
        return contact_deals
    except DealsApiException as e:
        return {"error": f"HubSpot Deals API error: {str(e)}"}

async def get_contact_conversations(contact_id: str) -> List[Dict]:
    """Get all conversations for a contact."""
    try:
        result = await asyncio.to_thread(
            client.conversations.visitor_identification.generate_token,
            email=contact_id
        )
        
        conversations = await asyncio.to_thread(
            client.conversations.visitor_identification.get_thread_list,
            token=result.token
        )
        
        return [conv.to_dict() for conv in conversations.results]
    except ConversationsApiException as e:
        return {"error": f"HubSpot Conversations API error: {str(e)}"}

async def get_contact_tickets(contact_id: str) -> List[Dict]:
    """Get all tickets associated with a contact."""
    try:
        result = await asyncio.to_thread(
            client.crm.tickets.basic_api.get_all,
            associations=["contacts"],
            properties=["subject", "content", "hs_pipeline_stage", "hs_ticket_priority"]
        )
        
        # Filter tickets for this contact
        contact_tickets = [
            ticket.to_dict() for ticket in result.results 
            if any(assoc.id == contact_id for assoc in ticket.associations.get("contacts", []))
        ]
        
        return contact_tickets
    except Exception as e:
        return {"error": f"HubSpot Tickets API error: {str(e)}"}

async def fetch_hubspot_data(email: str, resource: str, params: dict) -> dict:
    """
    Fetch data from HubSpot based on resource type.
    
    Args:
        email: Contact's email address
        resource: Type of data to fetch (contacts, deals, conversations, tickets)
        params: Additional parameters for filtering
    """
    try:
        # First get the contact to get the contact ID
        if resource == "contacts":
            contact_data = await find_contact_by_email(email)
            if not contact_data:
                return {"error": "Contact not found"}
            return contact_data
            
        contact_data = await find_contact_by_email(email)
        if not contact_data:
            return {"error": "Contact not found"}
        if "error" in contact_data:
            return contact_data
            
        contact_id = contact_data.get("id")
        if not contact_id:
            return {"error": "Contact not found"}
            
        # Fetch the requested resource
        if resource == "deals":
            return {"deals": await get_contact_deals(contact_id)}
        elif resource == "conversations":
            return {"conversations": await get_contact_conversations(contact_id)}
        elif resource == "tickets":
            return {"tickets": await get_contact_tickets(contact_id)}
        else:
            return {"error": f"Invalid resource type: {resource}"}
            
    except Exception as e:
        return {"error": f"Error fetching HubSpot data: {str(e)}"}

async def handle_mcp_call(body: MCPRequest) -> MCPResponse:
    """Handle MCP request by fetching appropriate HubSpot data."""
    key = f"{body.email}:{body.resource}:{str(body.params)}"
    cached = get_from_cache(key)
    if cached:
        return MCPResponse(data=cached, error=None)
    
    try:
        data = await fetch_hubspot_data(body.email, body.resource, body.params)
        if "error" in data:
            return MCPResponse(data={}, error=data["error"])
        set_in_cache(key, data)
        return MCPResponse(data=data, error=None)
    except Exception as e:
        return MCPResponse(data={}, error=str(e))
