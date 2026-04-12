"""FAQ knowledge base search tool."""

from typing import Annotated

from agent_framework import tool
from pydantic import Field

FAQ_DATABASE: dict[str, str] = {
    "return policy": (
        "You can return any item within 30 days of purchase for a full refund. "
        "Items must be in original condition with tags attached."
    ),
    "shipping": (
        "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days. "
        "Free shipping is available on orders over $50."
    ),
    "payment methods": (
        "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay. "
        "All transactions are processed securely."
    ),
    "business hours": (
        "Our customer support is available Monday through Friday, 9 AM to 6 PM EST. "
        "Email support is available 24/7."
    ),
    "warranty": (
        "All products come with a 1-year manufacturer warranty. "
        "Extended warranty options are available at checkout for an additional fee."
    ),
}


@tool(approval_mode="never_require")
def search_faq(
    query: Annotated[str, Field(description="The customer's question or topic to search for")],
) -> str:
    """Search the FAQ knowledge base for answers to common customer questions."""
    query_lower = query.lower()
    matches: list[str] = []

    for topic, answer in FAQ_DATABASE.items():
        if any(keyword in query_lower for keyword in topic.split()):
            matches.append(f"**{topic.title()}**: {answer}")

    if matches:
        return "\n\n".join(matches)
    return "No matching FAQ entries found. Please rephrase your question or ask to speak with a specialist."
