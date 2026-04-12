"""Handoff workflow — builds the multi-agent customer support orchestration."""

from agent_framework import Agent, Workflow
from agent_framework.orchestrations import HandoffBuilder


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
