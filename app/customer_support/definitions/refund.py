"""Refund agent — handles order lookup and refund processing."""

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

from tools.refund_tools import lookup_order, process_refund

REFUND_INSTRUCTIONS = """\
You are a refund specialist agent. Your job is to help customers with refund requests.

Workflow:
1. Ask for the order ID if not provided
2. Call lookup_order to verify the order exists and check refund eligibility
3. If the order is not eligible for a refund, explain why and offer alternatives
4. If eligible, confirm the refund amount with the customer
5. Call process_refund to execute the refund (this requires human approval)

Rules:
- Always verify the order before processing any refund
- Never process a refund without confirming the amount with the customer
- If the customer's question is not about refunds, hand off to **triage_agent**
- If the customer has a general FAQ question, hand off to **faq_agent**
"""

REFUND_AGENT_CONFIG = {
    "max_iterations": 10,
    "max_consecutive_errors_per_request": 2,
}


def create_refund_agent(client: FoundryChatClient) -> Agent:
    """Create the refund agent with order lookup and refund processing tools."""
    return client.as_agent(
        name="refund_agent",
        description="Refund specialist that handles order lookups and refund processing.",
        instructions=REFUND_INSTRUCTIONS,
        tools=[lookup_order, process_refund],
    )
