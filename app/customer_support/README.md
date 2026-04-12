# Customer Support System

A multi-agent customer support system built with **Microsoft Agent Framework** (`agent_framework`) and **Azure AI Foundry SDK v2** (`azure-ai-projects`). This sample demonstrates how to build a production-style support workflow where specialized agents collaborate through a handoff pattern to classify, answer, and process customer requests.

## What This Sample Demonstrates

- **Multi-agent orchestration** — Three specialized agents (Triage, FAQ, Refund) collaborate via a handoff workflow
- **Handoff pattern** — Bidirectional routing between agents using `HandoffBuilder`
- **Tool integration** — `@tool`-decorated Python functions for knowledge base search, order lookup, and refund processing
- **Human-in-the-loop** — The `process_refund` tool requires explicit human approval before execution
- **Input validation & error handling** — Typed exceptions, amount guards, and order existence checks
- **Foundry registration** — Optional script to register agent definitions in Azure AI Foundry

---

## Architecture

```
                    ┌──────────────────────────────────┐
                    │         Customer Input            │
                    └───────────────┬──────────────────┘
                                    │
                                    ▼
                           ┌────────────────┐
                           │  Triage Agent   │
                           │  (classifier)   │
                           └───┬─────────┬───┘
                               │         │
                    ┌──────────┘         └──────────┐
                    ▼                                ▼
           ┌────────────────┐              ┌────────────────┐
           │   FAQ Agent    │              │  Refund Agent  │
           │                │              │                │
           │  search_faq()  │              │ lookup_order() │
           │                │              │ process_refund │
           └────────────────┘              │  (approval)    │
                                           └────────────────┘
```

### Routing Topology

| Source | Targets | Description |
|--------|---------|-------------|
| Triage | FAQ, Refund | Routes classified inquiries to the appropriate specialist |
| FAQ | Triage, Refund | Hands back if the question is not FAQ-related |
| Refund | Triage, FAQ | Hands back if the request is not refund-related |

All handoffs are **bidirectional** — any agent can route back to Triage for reclassification, and cross-agent handoffs are supported through the triage fallback path.

---

## Agents

### Triage Agent

The entry point for all customer inquiries. Classifies messages into `faq`, `refund`, or `unknown` categories using rule-based instruction prompts.

- **Tools:** None (classification only)
- **Behavior:** Asks one clarifying question if the intent is unclear, then hands off

### FAQ Agent

Answers common customer questions by querying a built-in knowledge base.

- **Tools:** `search_faq`
- **Knowledge base topics:** Return policy, shipping times, payment methods, business hours, warranty
- **Behavior:** Always calls `search_faq` before answering; admits when no match is found

### Refund Agent

Handles refund requests with a structured verification-and-approval workflow.

- **Tools:** `lookup_order`, `process_refund`
- **Workflow:** Verify order → confirm amount with customer → process refund (requires approval)
- **Configuration:** `max_iterations=10`, `max_consecutive_errors_per_request=2`

---

## Tools Reference

| Tool | File | Description | Approval |
|------|------|-------------|----------|
| `search_faq` | `tools/knowledge_base.py` | Keyword-based search over a static FAQ dictionary | No |
| `lookup_order` | `tools/refund_tools.py` | Looks up an order by ID; returns JSON with amount, status, and refund eligibility | No |
| `process_refund` | `tools/refund_tools.py` | Processes a refund for a verified order; validates amount and order existence | **Yes** (`always_require`) |

### Input Validation (`process_refund`)

| Check | Behavior |
|-------|----------|
| `amount <= 0` | Returns error: "Refund amount must be greater than zero" |
| Order not found | Returns error: "Order {id} not found. Cannot process refund." |
| `amount > order.amount` | Returns error: "Refund amount exceeds order total" |

---

## Prerequisites

- **Python** ≥ 3.11
- **Azure CLI** authenticated (`az login`)
- An **Azure AI Foundry** project with a deployed chat model (e.g., `gpt-4o-mini`)

---

## Setup

### 1. Install dependencies

```bash
cd app/customer_support
pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
FOUNDRY_PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<project-name>
FOUNDRY_MODEL=gpt-4o-mini
```

### 3. Authenticate with Azure

```bash
az login
```

---

## How to Run

```bash
python main.py
```

The sample sends a hardcoded customer message (`"I want a refund for order #12345"`) through the workflow and streams the agent responses to stdout.

To change the input, edit the `user_input` variable in `main.py`.

---

## File Structure

```
customer_support/
├── pyproject.toml              # Project metadata & dependencies
├── .env.example                # Environment variable template
├── README.md                   # This file
│
├── definitions/                # Agent definitions (one file per agent)
│   ├── __init__.py
│   ├── triage.py               # Triage agent — classifies & routes inquiries
│   ├── faq.py                  # FAQ agent — knowledge base lookup
│   └── refund.py               # Refund agent — order lookup & refund processing
│
├── tools/                      # @tool-decorated functions
│   ├── __init__.py
│   ├── knowledge_base.py       # search_faq tool
│   └── refund_tools.py         # lookup_order & process_refund tools
│
├── workflow/                   # Orchestration logic
│   ├── __init__.py
│   └── handoff_workflow.py     # HandoffBuilder wiring
│
├── main.py                     # Entry point — assembles agents & runs workflow
└── register_agents.py          # (Optional) Register agents in Azure AI Foundry
```

### Dependency Flow

```
main.py → workflow/ → definitions/ → tools/
```

Strict one-way dependency: the workflow layer depends on definitions, which depend on tools. No circular imports.

---

## Security Features

### Human-in-the-Loop Approval

The `process_refund` tool is configured with `approval_mode="always_require"`. Every refund execution must be explicitly approved by a human operator before it proceeds.

### Input Validation

All tool inputs are validated before processing:
- Non-positive refund amounts are rejected
- Order existence is verified before processing
- Refund amounts exceeding the order total are rejected

### Error Handling

The system handles errors at the tool level with input validation guards:

- `process_refund` validates amount > 0, order existence, and amount ≤ order total
- `lookup_order` returns structured JSON errors for missing orders
- `search_faq` returns a fallback message when no matches are found

---

## Optional: Register Agents in Azure AI Foundry

To register the agent definitions as versioned resources in your Foundry project:

```bash
python register_agents.py
```

This uses the `azure-ai-projects` SDK to call `agents.create_version()` for each agent, creating named, versioned definitions that can be managed through the Foundry portal.

Registered agents:
- `customer-support-triage`
- `customer-support-faq`
- `customer-support-refund`

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `agent-framework[foundry,orchestrations]` | Agent creation, tool decorator, handoff workflow |
| `azure-ai-projects` | Foundry SDK v2 for agent registration |
| `azure-identity` | Azure authentication (CLI credentials) |
| `python-dotenv` | `.env` file loading |
