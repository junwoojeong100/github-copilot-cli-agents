"""Order lookup and refund processing tools."""

import json
from typing import Annotated

from agent_framework import tool
from pydantic import Field

ORDERS_DATABASE: dict[str, dict] = {
    "12345": {
        "order_id": "12345",
        "item": "Wireless Headphones",
        "amount": 129.99,
        "status": "delivered",
        "refund_eligible": True,
    },
    "67890": {
        "order_id": "67890",
        "item": "USB-C Charger",
        "amount": 29.99,
        "status": "in_transit",
        "refund_eligible": False,
    },
    "11111": {
        "order_id": "11111",
        "item": "Laptop Stand",
        "amount": 79.99,
        "status": "delivered",
        "refund_eligible": True,
    },
}


@tool(approval_mode="never_require")
def lookup_order(
    order_id: Annotated[str, Field(description="The order ID to look up")],
) -> str:
    """Look up an order by its ID. Returns order details including amount, status, and refund eligibility."""
    order = ORDERS_DATABASE.get(order_id)
    if order is None:
        return json.dumps({"error": f"Order {order_id} not found."})
    return json.dumps(order)


@tool(approval_mode="always_require")
def process_refund(
    order_id: Annotated[str, Field(description="The order ID to refund")],
    amount: Annotated[float, Field(description="The refund amount in dollars")],
) -> str:
    """Process a refund for a verified order. Requires human approval before execution."""
    if amount <= 0:
        return json.dumps({"error": "Refund amount must be greater than zero."})

    order = ORDERS_DATABASE.get(order_id)
    if order is None:
        return json.dumps({"error": f"Order {order_id} not found. Cannot process refund."})

    if amount > order["amount"]:
        return json.dumps({
            "error": f"Refund amount ${amount:.2f} exceeds order total ${order['amount']:.2f}."
        })

    return json.dumps({
        "status": "refund_processed",
        "order_id": order_id,
        "refund_amount": amount,
        "message": f"Refund of ${amount:.2f} processed successfully for order {order_id}.",
    })
