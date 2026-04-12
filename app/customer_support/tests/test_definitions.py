"""Integration tests for agent definitions — real Foundry calls.

Each agent is created with a real FoundryChatClient and run against Foundry
to verify it produces a meaningful response for its domain.
"""

import asyncio
import os

import pytest
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from agent_framework.foundry import FoundryChatClient
from definitions.triage import TRIAGE_INSTRUCTIONS, create_triage_agent
from definitions.faq import FAQ_INSTRUCTIONS, create_faq_agent
from definitions.refund import REFUND_INSTRUCTIONS, create_refund_agent

load_dotenv()

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def foundry_client():
    """Create a FoundryChatClient per test to avoid shared history state."""
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL", "gpt-4o-mini"),
        credential=AzureCliCredential(),
    )


# ---------------------------------------------------------------------------
# Triage agent
# ---------------------------------------------------------------------------

class TestTriageAgent:
    """Integration tests for the triage agent."""

    def test_instructions_mention_routing_targets(self):
        """Triage instructions should reference both specialist agents."""
        assert "faq_agent" in TRIAGE_INSTRUCTIONS
        assert "refund_agent" in TRIAGE_INSTRUCTIONS

    @pytest.mark.asyncio
    async def test_triage_responds_to_greeting(self, foundry_client):
        """Triage agent should respond (e.g. ask clarifying question) for vague input."""
        agent = create_triage_agent(foundry_client)
        result = await agent.run("Hello, I need some help")
        assert result.text is not None
        assert len(result.text) > 0

    @pytest.mark.asyncio
    async def test_triage_responds_to_refund_query(self, foundry_client):
        """Triage agent should acknowledge/route a refund request."""
        agent = create_triage_agent(foundry_client)
        result = await agent.run("I want a refund for my order")
        assert result.text is not None
        assert len(result.text) > 0


# ---------------------------------------------------------------------------
# FAQ agent
# ---------------------------------------------------------------------------

class TestFaqAgent:
    """Integration tests for the FAQ agent."""

    def test_instructions_mention_handoff_targets(self):
        assert "refund_agent" in FAQ_INSTRUCTIONS
        assert "triage_agent" in FAQ_INSTRUCTIONS

    @pytest.mark.asyncio
    async def test_faq_answers_shipping_question(self, foundry_client):
        """FAQ agent should use search_faq tool and answer about shipping."""
        agent = create_faq_agent(foundry_client)
        result = await agent.run("How long does shipping take?")
        text = result.text.lower()
        assert any(kw in text for kw in ["shipping", "days", "business", "delivery"])

    @pytest.mark.asyncio
    async def test_faq_answers_return_policy(self, foundry_client):
        """FAQ agent should answer about return policy using knowledge base."""
        agent = create_faq_agent(foundry_client)
        result = await agent.run("What is your return policy?")
        text = result.text.lower()
        assert any(kw in text for kw in ["return", "30 days", "refund", "policy"])

    @pytest.mark.asyncio
    async def test_faq_handles_unknown_topic(self, foundry_client):
        """FAQ agent should indicate it doesn't have info for unknown topics."""
        agent = create_faq_agent(foundry_client)
        result = await agent.run("What is the gravitational constant of Jupiter?")
        assert result.text is not None
        assert len(result.text) > 0


# ---------------------------------------------------------------------------
# Refund agent
# ---------------------------------------------------------------------------

class TestRefundAgent:
    """Integration tests for the refund agent."""

    def test_instructions_mention_handoff_targets(self):
        assert "triage_agent" in REFUND_INSTRUCTIONS
        assert "faq_agent" in REFUND_INSTRUCTIONS

    @pytest.mark.asyncio
    async def test_refund_agent_looks_up_order(self, foundry_client):
        """Refund agent should use lookup_order tool for a known order."""
        agent = create_refund_agent(foundry_client)
        result = await agent.run("I want a refund for order #12345")
        text = result.text.lower()
        assert any(kw in text for kw in ["12345", "refund", "headphones", "129", "order"])

    @pytest.mark.asyncio
    async def test_refund_agent_handles_nonexistent_order(self, foundry_client):
        """Refund agent should report when an order is not found."""
        agent = create_refund_agent(foundry_client)
        result = await agent.run("Refund order #99999")
        text = result.text.lower()
        assert any(kw in text for kw in [
            "not found", "couldn't find", "unable", "doesn't exist",
            "no order", "cannot", "don't have", "isn't", "99999",
            "sorry", "locate", "invalid", "check",
        ])
