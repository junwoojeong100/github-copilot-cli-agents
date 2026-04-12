"""Entry point — assembles agents, builds workflow, and runs the customer support system."""

import asyncio
import os

from agent_framework import Content, WorkflowEvent
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import HandoffAgentUserRequest
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from definitions import create_faq_agent, create_refund_agent, create_triage_agent
from workflow import build_support_workflow


async def main() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_MODEL", "gpt-4o-mini")

    client = FoundryChatClient(
        project_endpoint=endpoint,
        model=model,
        credential=AzureCliCredential(),
    )

    # Create agents
    triage_agent = create_triage_agent(client)
    faq_agent = create_faq_agent(client)
    refund_agent = create_refund_agent(client)

    # Build workflow
    workflow = build_support_workflow(triage_agent, faq_agent, refund_agent)

    # Sample customer input
    user_input = "I want a refund for order #12345"
    print(f"\n{'='*60}")
    print(f"Customer: {user_input}")
    print(f"{'='*60}\n")

    pending_requests: list[WorkflowEvent] = []

    # Start workflow
    async for event in workflow.run_stream(user_input):
        if event.type == "request_info":
            pending_requests.append(event)
        elif event.type == "output":
            for msg in event.data.messages:
                if msg.text:
                    print(f"[{msg.author_name or 'System'}]: {msg.text}")

    # Handle pending requests (user input & tool approvals)
    while pending_requests:
        responses: dict[str, object] = {}

        for request in pending_requests:
            if isinstance(request.data, HandoffAgentUserRequest):
                print(f"\nAgent {request.executor_id} asks:")
                for msg in request.data.agent_response.messages[-2:]:
                    if msg.text:
                        print(f"  {msg.author_name}: {msg.text}")

                user_reply = input("You: ")
                responses[request.request_id] = HandoffAgentUserRequest.create_response(user_reply)

            elif isinstance(request.data, Content) and request.data.type == "function_approval_request":
                func_call = request.data.function_call
                args = func_call.parse_arguments() or {}

                print(f"\n⚠️  Tool approval requested: {func_call.name}")
                print(f"   Arguments: {args}")

                approval = input("Approve? (y/n): ").strip().lower() == "y"
                responses[request.request_id] = request.data.to_function_approval_response(approved=approval)

        pending_requests = []
        async for event in workflow.run(responses=responses):
            if event.type == "request_info":
                pending_requests.append(event)
            elif event.type == "output":
                for msg in event.data.messages:
                    if msg.text:
                        print(f"[{msg.author_name or 'System'}]: {msg.text}")

    print(f"\n{'='*60}")
    print("Workflow completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
