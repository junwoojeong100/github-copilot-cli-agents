"""(Optional) Register agent definitions in Azure AI Foundry as versioned resources."""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

AGENT_DEFINITIONS = [
    {
        "name": "customer-support-triage",
        "instructions": "Classify customer inquiries into faq/refund/unknown and route accordingly.",
    },
    {
        "name": "customer-support-faq",
        "instructions": "Answer common questions using the search_faq tool. Admit when no match is found.",
    },
    {
        "name": "customer-support-refund",
        "instructions": "Verify orders with lookup_order, then process refunds with process_refund (requires approval).",
    },
]


def register_all() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_MODEL", "gpt-4o-mini")

    if "/api/projects/" not in endpoint:
        print("⚠️  FOUNDRY_PROJECT_ENDPOINT must include the project path for agent registration.")
        print("   Expected format: https://<resource>.services.ai.azure.com/api/projects/<project-name>")
        print(f"   Current value:   {endpoint}")
        print("\n   Agent registration requires an Azure AI Foundry project.")
        print("   The main workflow (main.py) works without a project path.")
        return

    client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    for agent_def in AGENT_DEFINITIONS:
        result = client.agents.create_version(
            agent_name=agent_def["name"],
            definition=PromptAgentDefinition(
                model=model,
                instructions=agent_def["instructions"],
            ),
        )
        print(f"✅ Registered: {result.name} (id={result.id}, version={result.version})")


if __name__ == "__main__":
    register_all()
