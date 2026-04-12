"""(Optional) Register agent definitions in Azure AI Foundry as versioned resources."""

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

AGENT_DEFINITIONS = [
    {
        "name": "customer-support-triage",
        "description": "Triage agent that classifies customer inquiries and routes to specialists.",
        "instructions": "Classify customer inquiries into faq/refund/unknown and route accordingly.",
    },
    {
        "name": "customer-support-faq",
        "description": "FAQ specialist that answers common customer questions using a knowledge base.",
        "instructions": "Answer common questions using the search_faq tool. Admit when no match is found.",
    },
    {
        "name": "customer-support-refund",
        "description": "Refund specialist that handles order lookups and refund processing.",
        "instructions": "Verify orders with lookup_order, then process refunds with process_refund (requires approval).",
    },
]


def register_all() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    for agent_def in AGENT_DEFINITIONS:
        result = client.agents.create_agent(
            model=os.environ.get("FOUNDRY_MODEL", "gpt-4o-mini"),
            name=agent_def["name"],
            instructions=agent_def["instructions"],
        )
        print(f"✅ Registered: {agent_def['name']} (id={result.id})")


if __name__ == "__main__":
    register_all()
