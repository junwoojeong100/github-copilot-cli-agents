"""Handoff workflow — builds the multi-agent customer support orchestration."""

from agent_framework import Agent, Message, Workflow
from agent_framework.orchestrations import HandoffBuilder


def _termination_condition(conversation: list[Message]) -> bool:
    """Terminate when the customer indicates they're done."""
    if not conversation:
        return False
    for msg in reversed(conversation[-4:]):
        text = (msg.text or "").strip().lower()
        if msg.role == "user" and any(
            phrase in text
            for phrase in ["thank", "that's all", "no more", "goodbye", "bye", "done", ""]
        ):
            # Check if the assistant already said goodbye
            for later_msg in reversed(conversation):
                if later_msg.role == "assistant" and any(
                    w in (later_msg.text or "").lower()
                    for w in ["welcome", "great day", "take care", "goodbye"]
                ):
                    return True
            break
    return False


def build_support_workflow(
    triage_agent: Agent,
    faq_agent: Agent,
    refund_agent: Agent,
) -> Workflow:
    """Build a handoff workflow with bidirectional routing between all agents.

    Routing topology:
        Triage → FAQ, Refund   (routes classified inquiries)
        FAQ    → Triage, Refund (hands back if not FAQ-related)
        Refund → Triage, FAQ   (hands back if not refund-related)
    """
    workflow = (
        HandoffBuilder(
            name="customer_support_handoff",
            participants=[triage_agent, faq_agent, refund_agent],
            termination_condition=_termination_condition,
        )
        .with_start_agent(triage_agent)
        .add_handoff(triage_agent, [faq_agent], description="Route FAQ questions to the FAQ specialist.")
        .add_handoff(triage_agent, [refund_agent], description="Route refund requests to the refund specialist.")
        .add_handoff(faq_agent, [triage_agent], description="Hand back to triage for reclassification.")
        .add_handoff(faq_agent, [refund_agent], description="Route refund requests to the refund specialist.")
        .add_handoff(refund_agent, [triage_agent], description="Hand back to triage for reclassification.")
        .add_handoff(refund_agent, [faq_agent], description="Route FAQ questions to the FAQ specialist.")
        .build()
    )
    return workflow
