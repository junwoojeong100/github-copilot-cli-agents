"""Integration tests for the handoff workflow — real Foundry calls.

Tests the full workflow: triage → specialist routing, output quality,
and the termination condition (pure logic, no Foundry needed).
"""

import os
from unittest.mock import MagicMock

import pytest
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from agent_framework import Message
from agent_framework.foundry import FoundryChatClient
from definitions import create_faq_agent, create_refund_agent, create_triage_agent
from workflow.handoff_workflow import _termination_condition, build_support_workflow

load_dotenv()

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def foundry_client():
    """Create a fresh FoundryChatClient per test to avoid shared history state."""
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL", "gpt-4o-mini"),
        credential=AzureCliCredential(),
    )


@pytest.fixture
def support_workflow(foundry_client):
    """Build a fresh support workflow per test (agents use InMemoryHistoryProvider)."""
    triage = create_triage_agent(foundry_client)
    faq = create_faq_agent(foundry_client)
    refund = create_refund_agent(foundry_client)
    return build_support_workflow(triage, faq, refund)


# ---------------------------------------------------------------------------
# _termination_condition (pure logic — no Foundry)
# ---------------------------------------------------------------------------

class TestTerminationCondition:
    """Tests for the conversation termination logic."""

    @staticmethod
    def _msg(role: str, text: str) -> Message:
        msg = MagicMock(spec=Message)
        msg.role = role
        msg.text = text
        return msg

    def test_empty_conversation(self):
        assert _termination_condition([]) is False

    def test_user_thanks_without_assistant_goodbye(self):
        convo = [self._msg("user", "thank you")]
        assert _termination_condition(convo) is False

    def test_user_thanks_with_assistant_goodbye(self):
        convo = [
            self._msg("user", "thank you"),
            self._msg("assistant", "You're welcome! Have a great day!"),
        ]
        assert _termination_condition(convo) is True

    def test_user_says_bye_with_assistant_goodbye(self):
        convo = [
            self._msg("user", "goodbye"),
            self._msg("assistant", "Take care! Goodbye!"),
        ]
        assert _termination_condition(convo) is True

    def test_user_says_done_with_assistant_farewell(self):
        convo = [
            self._msg("user", "done"),
            self._msg("assistant", "You're welcome! Have a great day!"),
        ]
        assert _termination_condition(convo) is True

    def test_user_says_thats_all_with_farewell(self):
        convo = [
            self._msg("user", "that's all"),
            self._msg("assistant", "Take care!"),
        ]
        assert _termination_condition(convo) is True

    def test_ongoing_conversation_no_termination(self):
        convo = [
            self._msg("user", "I need help with my order"),
            self._msg("assistant", "Sure, let me look that up for you."),
        ]
        assert _termination_condition(convo) is False

    def test_mixed_conversation_terminates_at_end(self):
        convo = [
            self._msg("user", "I need a refund"),
            self._msg("assistant", "Let me check your order."),
            self._msg("user", "thanks, that's all"),
            self._msg("assistant", "You're welcome! Have a great day!"),
        ]
        assert _termination_condition(convo) is True

    def test_empty_user_message_with_goodbye(self):
        convo = [
            self._msg("user", ""),
            self._msg("assistant", "Have a great day! Take care."),
        ]
        assert _termination_condition(convo) is True


# ---------------------------------------------------------------------------
# Workflow integration: FAQ routing
# ---------------------------------------------------------------------------

class TestWorkflowFaqRouting:
    """Verify FAQ queries are routed through triage → faq_agent."""

    @pytest.mark.asyncio
    async def test_faq_query_produces_output(self, support_workflow):
        """A FAQ question should produce at least one output with relevant content."""
        result = await support_workflow.run("What is your return policy?")
        outputs = result.get_outputs()
        assert len(outputs) >= 1

        all_text = " ".join(o.text for o in outputs if o.text)
        assert any(kw in all_text.lower() for kw in ["return", "30 days", "refund", "policy"])

    @pytest.mark.asyncio
    async def test_faq_query_invokes_faq_agent(self, support_workflow):
        """FAQ question should be handled by the faq_agent."""
        result = await support_workflow.run("How long does shipping take?")
        invoked_agents = {e.executor_id for e in result if e.type == "executor_invoked"}
        assert "faq_agent" in invoked_agents

    @pytest.mark.asyncio
    async def test_faq_query_starts_with_triage(self, support_workflow):
        """All queries should start with the triage agent."""
        result = await support_workflow.run("What payment methods do you accept?")
        first_invoked = next(e for e in result if e.type == "executor_invoked")
        assert first_invoked.executor_id == "triage_agent"


# ---------------------------------------------------------------------------
# Workflow integration: Refund routing
# ---------------------------------------------------------------------------

class TestWorkflowRefundRouting:
    """Verify refund queries are routed through triage → refund_agent."""

    @pytest.mark.asyncio
    async def test_refund_query_invokes_refund_agent(self, support_workflow):
        """A refund request should reach the refund_agent."""
        result = await support_workflow.run("I want a refund for order #12345")
        invoked_agents = {e.executor_id for e in result if e.type == "executor_invoked"}
        assert "refund_agent" in invoked_agents

    @pytest.mark.asyncio
    async def test_refund_query_produces_order_details(self, support_workflow):
        """Refund request for a known order should include order information."""
        result = await support_workflow.run("I need a refund for order #12345")
        outputs = result.get_outputs()
        all_text = " ".join(o.text for o in outputs if o.text)
        assert any(kw in all_text.lower() for kw in ["12345", "refund", "129", "headphones"])

    @pytest.mark.asyncio
    async def test_refund_nonexistent_order(self, support_workflow):
        """Refund request for a nonexistent order should communicate the error."""
        result = await support_workflow.run("Refund order #99999 please")
        outputs = result.get_outputs()
        all_text = " ".join(o.text for o in outputs if o.text).lower()
        assert any(kw in all_text for kw in [
            "not found", "couldn't find", "unable", "doesn't exist",
            "no order", "cannot", "don't have", "isn't", "99999",
            "sorry", "locate", "invalid", "check",
        ])


# ---------------------------------------------------------------------------
# Workflow integration: Handoff events
# ---------------------------------------------------------------------------

class TestWorkflowHandoffEvents:
    """Verify handoff mechanics in the workflow event stream."""

    @pytest.mark.asyncio
    async def test_handoff_event_emitted(self, support_workflow):
        """A query requiring specialist should emit a handoff_sent event."""
        result = await support_workflow.run("What is your warranty policy?")
        event_types = {e.type for e in result}
        assert "handoff_sent" in event_types

    @pytest.mark.asyncio
    async def test_workflow_completes_without_error(self, support_workflow):
        """Workflow should not produce any error events for a normal query."""
        result = await support_workflow.run("Tell me about your business hours")
        error_events = [e for e in result if e.type in ("error", "failed", "executor_failed")]
        assert len(error_events) == 0
