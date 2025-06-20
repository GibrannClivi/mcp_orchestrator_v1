"""
Business logic for Chargebee MCP microservice.
"""
import asyncio
import os
from typing import Optional

import chargebee
from cachetools import TTLCache
from dotenv import load_dotenv

from src.mcp_servers.common.models import ChargebeeCustomer

load_dotenv()


class ChargebeeService:
    def __init__(self):
        chargebee.configure(
            os.environ["CHARGEBEE_API_KEY"], os.environ["CHARGEBEE_SITE"]
        )
        self.cache = TTLCache(maxsize=1000, ttl=300)

    async def get_customer_details_by_email(
        self, email: str
    ) -> Optional[ChargebeeCustomer]:
        cached_result = self.cache.get(email)
        if cached_result:
            return cached_result

        try:
            # Fetch customer by email
            customers = await asyncio.to_thread(
                chargebee.Customer.list, {"email[is]": email}
            )
            if not customers:
                return None

            customer_data = customers[0].customer
            customer_id = customer_data.id

            # Fetch subscriptions for the customer
            subscriptions_result = await asyncio.to_thread(
                chargebee.Subscription.list, {"customer_id[is]": customer_id}
            )
            subscriptions = [entry.subscription for entry in subscriptions_result]

            # Fetch invoices for history
            invoices_result = await asyncio.to_thread(
                chargebee.Invoice.list, {"customer_id[is]": customer_id}
            )
            invoices = [entry.invoice for entry in invoices_result]

            # Assume the first subscription is the primary one for this simplified example
            primary_subscription = subscriptions[0] if subscriptions else None

            customer_details = ChargebeeCustomer(
                email=customer_data.email,
                name=f"{customer_data.first_name} {customer_data.last_name}",
                hubspot_crm_id=customer_data.cf_hubspot_id
                if hasattr(customer_data, "cf_hubspot_id")
                else None,
                plan=primary_subscription.plan_id if primary_subscription else "N/A",
                payment_terms=primary_subscription.po_number
                if primary_subscription
                else "N/A",
                next_billing_on=primary_subscription.next_billing_at
                if primary_subscription
                else None,
                subscription_id=primary_subscription.id
                if primary_subscription
                else "N/A",
                subscription_status=primary_subscription.status
                if primary_subscription
                else "N/A",
                history=[
                    {
                        "date": inv.paid_at if inv.paid_at else inv.date,
                        "amount": inv.amount_paid / 100.0,
                        "status": inv.status,
                    }
                    for inv in invoices
                ],
            )

            self.cache[email] = customer_details
            return customer_details

        except Exception as e:
            # In a real app, you'd want more robust logging and error handling
            print(f"An error occurred: {e}")
            return None
