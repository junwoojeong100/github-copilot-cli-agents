"""FAQ agent — answers common customer questions using knowledge base."""

from agent_framework import Agent, InMemoryHistoryProvider
from agent_framework.foundry import FoundryChatClient

from tools.knowledge_base import search_faq

FAQ_INSTRUCTIONS = """\
You are a FAQ specialist agent. Your job is to answer common customer questions \
using the knowledge base.

Rules:
- ALWAYS call the search_faq tool before answering any question
- Base your answer on the tool results — do not fabricate information
- If search_faq returns no results, honestly tell the customer you don't have \
  that information and offer to hand off to another agent
- If the customer's question is about refunds or order issues, hand off to **refund_agent**
- If the question doesn't fit your expertise, hand off back to **triage_agent**
"""


def create_faq_agent(client: FoundryChatClient) -> Agent:
    """Create the FAQ agent with knowledge base search tool."""
    return Agent(
        client=client,
        name="faq_agent",
        description="FAQ specialist that answers common customer questions using a knowledge base.",
        instructions=FAQ_INSTRUCTIONS,
        tools=[search_faq],
        context_providers=[InMemoryHistoryProvider("faq_history", load_messages=True)],
        require_per_service_call_history_persistence=True,
    )
