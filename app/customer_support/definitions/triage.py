"""Triage agent — classifies and routes customer inquiries."""

from agent_framework import Agent, InMemoryHistoryProvider
from agent_framework.foundry import FoundryChatClient

TRIAGE_INSTRUCTIONS = """\
You are a customer support triage agent. Your job is to classify incoming customer \
inquiries and route them to the appropriate specialist agent.

Classification rules:
- If the customer has a question about policies, shipping, payments, hours, or warranty → hand off to **faq_agent**
- If the customer wants a refund, mentions an order problem, or requests money back → hand off to **refund_agent**
- If the intent is unclear, ask ONE clarifying question before routing

Always be polite and professional. Never attempt to answer questions yourself — \
always route to the appropriate specialist.
"""


def create_triage_agent(client: FoundryChatClient) -> Agent:
    """Create the triage agent that classifies and routes inquiries."""
    return Agent(
        client=client,
        name="triage_agent",
        description="Triage agent that classifies customer inquiries and routes to specialists.",
        instructions=TRIAGE_INSTRUCTIONS,
        context_providers=[InMemoryHistoryProvider("triage_history", load_messages=True)],
        require_per_service_call_history_persistence=True,
    )
