# Chapter 3: Enterprise Deep Research & Synthesis

This chapter analyzes the "Grand Finale" architecture: the **Deep Research Agent**. This is where we move from single errands to a complex, multi-agent hierarchy capable of autonomous, long-form report generation.

---

## 1. The Architectural Hierarchy
For enterprise-grade reliability, we don't use 1 agent. We use 6 specialized agents:

1. **ClarifyAgent:** (The Discovery Phase) Interviews the user to eliminate ambiguity.
2. **ResearchManager:** (The Orchestrator) The brain that coordinates the workflow.
3. **PlannerAgent:** (The Architect) Breaks the 5-point research goal into tasks.
4. **SearchAgent:** (The Researcher) Calls tools like Tavily to crawl the web.
5. **WriterAgent:** (The Editor) Synthesizes raw data into professional markdown.
6. **EmailAgent:** (The Dispatcher) Delivers the final report to the stakeholder.

---

## 2. The Two-Step Discovery Logic
Research fails when the goal is vague. We implement a **Two-Step Workflow**:

### Step 1: Clarification (The Interview)
The `ClarifyAgent` uses a specialized prompt to ask EXACTLY 3 targeted questions based on the user's initial prompt.

### Step 2: Execution (The Research)
Only once the user provides details, the `ResearchManager` is triggered. We pass the *initial prompt* + the *answers* as a combined context.

```python
# Logic for combining state
combined_context = f"Initial Goal: {user_goal}\nClarification Answers: {user_answers}"
await Runner.run(research_manager, combined_context)
```

---

## 3. Streaming & Async Production UIs
Research can take 60-120 seconds. If the UI stays static, the user assumes it's crashed. We use `Runner.run_streamed()` to provide real-time updates.

### Hooking into Stream Events:
By monitoring `RunItemStreamEvent`, we can update a Gradio progress bar or text box asynchronously.

```python
result_stream = Runner.run_streamed(manager, input)

async for event in result_stream.stream_events():
    if event.type == "call_tool_event":
        yield f"Agent is currently: {event.data.function.name}..."
    elif event.type == "raw_response_event":
        # Stream the actual text as it's being generated
        yield event.data.delta
```

---

---

## 4. Framework Comparison Summary
As an AI Agency owner, you must choose the right tool for the specific client problem:

| Framework | Mental Model | Best For... |
| :--- | :--- | :--- |
| **OpenAI SDK** | **Developer-First** | Fine-grained control, custom tools, and strict logic. Perfect for software integrations. |
| **CrewAI** | **Role-First** | "Colloquial" agents that collaborate autonomously. Best for creative tasks and complex team simulations. |
| **LangGraph** | **Flow-First** | Cyclic graphs and state persistence. Best for long-running, multi-day stateful agents. |

---

### Final Blueprint: The "Agency Standard" Agent
A professional-grade agent implementation must satisfy these 4 requirements:
1. **Zero Hallucination:** Always call a search tool for data >6 months old.
2. **Transparent Tracing:** Use `trace()` to show the client exactly how their tokens were spent.
3. **Structured Handoffs:** Use specialists (Search, Email, Code) instead of one "Generalist" agent.
4. **Deterministic Output:** Use Pydantic to ensure the report format never breaks.

---

> [!CAUTION]
> **Production Warning:**
> When deploying these multi-agent systems, always implement **Rate Limiting** and **Token Budgets**. A rogue Planner-Search loop can consume hundreds of dollars in API credits if not capped.

---

## Progress Log

### 2026-04-26 — First Live Run: Israel-US Tensions & UAE Travel Impact
- Successfully executed the full deep research pipeline via `uv run` on Python 3.9 (needed `eval_type_backport` for typing compatibility)
- Pipeline: ManagerAgent → Planner (5 search queries) → Search (Tavily SDK, 5 concurrent searches) → Writer (19K markdown report) → Email agent (sent successfully)
- **Topic**: Israel-US tensions April 2026, impact on UAE flights, airspace, WFH policies, travel advisories
- **Report**: 19,106 chars, 313 lines, 8 sections with executive summary, data tables, and checklist
- **Report saved** to `deep_research_my_version/UAE_Travel_Report_April_2026.md`
- Key learnings: DeepSeek-Chat handles the full pipeline well via OpenAI-compatible SDK. Tavily SDK works for real-time web data. `set_tracing_disabled(True)` required to prevent DeepSeek key from hitting OpenAI's tracing endpoint.
