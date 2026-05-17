# Email CRM Agent

**Date:** 2026-04-25

## 1. Project Overview

The **Email CRM Agent** is an intelligent email management and client relationship system built with the OpenAI Agents SDK. It fetches emails from Gmail/Outlook, groups them into conversations, and generates comprehensive client summaries with engagement insights.

**Core Problem Solved:** Turns raw email data into actionable client intelligence — tracking relationship history, engagement patterns, and recommended next steps without manual CRM data entry.

---

## 2. Technical Architecture

### The Core Components

| Component | Purpose | Key Feature |
| :--- | :--- | :--- |
| **ManagerAgent** | Orchestrator | Coordinates all sub-agents via tools and handoffs |
| **EmailRetrieverAgent** | Email Fetching | Gmail/Outlook API integration with filtering |
| **ConversationProcessorAgent** | Thread Grouping | Groups emails by thread, extracts clients |
| **ClientSummarizerAgent** | Analytics | Generates engagement scores and insights |

### Architecture Pattern: Manager-Specialist Pipeline

```
User Query
    ↓
ManagerAgent (orchestrator with tools)
    ↓ (tool calls)
EmailRetriever → ConversationProcessor → ClientSummarizer
    ↓
Structured Output (client summary, conversation threads)
```

### Agent Communication

- **Tools vs Handoffs:** Sub-agents are mounted as tools (`.as_tool()`) on the Manager, not handoffs. The Manager calls them and receives results to continue orchestration.
- **DeepSeek Backend:** All agents use `deepseek-chat` via `OpenAIChatCompletionsModel` with custom client

---

## 3. Implementation Details

### Step 1: DeepSeek Client Setup Pattern

```python
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel

deepseek_api_key = os.getenv("deepseek_api_key", "")
os.environ["OPENAI_API_KEY"] = deepseek_api_key  # OpenAI SDK compat

deepseek_client = AsyncOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=deepseek_api_key
)
deepseek_model = OpenAIChatCompletionsModel(
    model="deepseek-chat",
    openai_client=deepseek_client
)
```

> [!TIP]
> This pattern (setting `OPENAI_API_KEY` env var + using `AsyncOpenAI` with DeepSeek base URL) is the standard way to use DeepSeek with the OpenAI Agents SDK. The SDK treats DeepSeek as an OpenAI-compatible endpoint.

### Step 2: Manager Agent with Tool Mounting

```python
manager_agent = Agent(
    name="EmailCRMManager",
    instructions=MANAGER_INSTRUCTIONS,
    model=deepseek_model,
    tools=[
        email_retriever_agent.as_tool(
            tool_name="EmailRetriever",
            tool_description="Fetches emails from Gmail or Outlook based on criteria"
        ),
        conversation_processor_agent.as_tool(
            tool_name="ConversationProcessor",
            tool_description="Groups emails into conversations, extracts clients"
        ),
        client_summarizer_agent.as_tool(
            tool_name="ClientSummarizer",
            tool_description="Generates comprehensive client summaries"
        ),
    ],
)
```

### Step 3: Database Models (SQLAlchemy ORM)

The system uses 5 core models:

| Model | Purpose | Key Fields |
| :--- | :--- | :--- |
| **Client** | Unique contacts | name, email, company, phone, first_contact, last_contact |
| **Email** | Raw messages | message_id, sender, recipient, subject, body, timestamp |
| **Conversation** | Thread grouping | thread_id, topic, summary, start_date, message_count |
| **Interaction** | Key moments | interaction_type, date, sentiment, keywords |
| **Analytics** | Pre-computed stats | engagement_score, avg_response_time, last_30_days_count |

### Step 4: Email Provider Integration

```python
async def retrieve_emails_gmail(filters: dict) -> dict:
    # Placeholder - requires OAuth setup
    return {
        "status": "success",
        "provider": "gmail",
        "emails": [],
        "count": 0,
        "message": "Gmail integration requires OAuth setup in config/"
    }

async def retrieve_emails_outlook(filters: dict) -> dict:
    # Placeholder - requires OAuth setup
    return {
        "status": "success",
        "provider": "outlook",
        "emails": [],
        "count": 0,
        "message": "Outlook integration requires OAuth setup in config/"
    }
```

### Step 5: Client Summarization Output Format

```python
{
    'client_name': 'John Smith',
    'client_email': 'john@example.com',
    'first_contact': '2025-01-15',
    'last_contact': '2026-03-20',
    'total_conversations': 12,
    'total_emails': 45,
    'topics': ['Project Discussion', 'Budget', 'Timeline'],
    'timeline': [{'date': '2025-01-15', 'event': 'Initial contact...'}],
    'context': 'Comprehensive summary of relationship...',
    'engagement_score': 8.5,
    'recommended_actions': ['Follow up on proposal', '...']
}
```

---

## 4. Key Design Principles Learned

1. **Manager-Specialist pattern for orchestration.** The Manager doesn't do the work — it coordinates specialists via tool calls and receives results back.
2. **Tool mounting via `.as_tool()`** allows the Manager to call sub-agents and continue with their output. Handoffs would transfer control permanently.
3. **DeepSeek via OpenAI SDK compatibility.** Setting `OPENAI_API_KEY` to DeepSeek key + using `AsyncOpenAI` with DeepSeek base URL makes all SDK features work seamlessly.
4. **Placeholder providers are architectural scaffolding.** The Gmail/Outlook integrations are documented as requiring OAuth — this is intentional to show where real API integration would go.
5. **SQLAlchemy ORM for data integrity.** Using proper relationships (`client.emails`, `conversation.emails`) ensures referential integrity across the system.
6. **Engagement scoring is multi-dimensional.** Score combines frequency, recency, sentiment, and conversation duration — not just email count.

---

## 5. Errors Encountered & Fixes

### No Errors Recorded Yet

This project is in active development. Placeholder functions for Gmail/Outlook API integration await OAuth setup.

---

## 6. Configuration Reference

### Environment Variables

| Variable | Purpose | Status |
| :--- | :--- | :--- |
| `deepseek_api_key` | DeepSeek API authentication | Required |
| `OPENAI_API_KEY` | Set equal to deepseek_api_key for SDK compatibility | Required |
| `DATABASE_URL` | SQLAlchemy connection string | Optional (defaults to SQLite) |

### Manager Instructions (Workflows)

```python
MANAGER_INSTRUCTIONS = (
    "You are the Master Orchestrator for the Email CRM Agent system.\n"
    "Available operations:\n\n"
    "1. RETRIEVE_EMAILS - Fetch emails from inbox/sent\n"
    "2. PROCESS_EMAILS - Convert to conversations\n"
    "3. SUMMARIZE_CLIENT - Get client insights\n"
    "4. LIST_CLIENTS - Get all clients\n\n"
    "Workflow examples:\n"
    "Example 1 - New retrieval: 'Get 100 emails from inbox from gmail from last 30 days'\n"
    "Example 2 - Client summary: 'Summarize John Smith'\n"
)
```

---

## 7. Running the Project

```bash
# Entry point (when app.py is created)
uv run python agents/manager_agent.py

# Or when integrated with main app
uv run email_crm_agent
```

---

## 8. Output Architecture

| Output | Source | Purpose |
| :--- | :--- | :--- |
| **Client Profiles** | ClientSummarizerAgent | name, email, engagement_score, recommended_actions |
| **Conversation Threads** | ConversationProcessorAgent | thread_id, topic, summary, message_count |
| **Raw Emails** | EmailRetrieverAgent | Full email objects with metadata |
| **Analytics** | Analytics model | Pre-computed engagement metrics |

---

## 9. Project Structure

```
Email CRM Agent/
├── agents/
│   ├── manager_agent.py           # Main orchestrator
│   ├── email_retriever_agent.py  # Gmail/Outlook fetching
│   ├── conversation_processor_agent.py  # Thread grouping
│   └── client_summarizer_agent.py  # Client insights
├── database/
│   └── models.py                  # SQLAlchemy ORM models
└── .env                           # API keys
```

---

## 10. TODO / Next Steps

- [ ] Complete Gmail OAuth integration
- [ ] Complete Outlook Graph API integration
- [ ] Add Gradio UI for the Manager agent
- [ ] Implement streaming responses for email retrieval
- [ ] Add Pydantic output validation for structured client summaries
- [ ] Build conversation timeline visualization