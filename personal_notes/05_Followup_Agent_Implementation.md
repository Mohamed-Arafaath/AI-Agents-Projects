# Chapter 5: Followup Agent — Context-Aware Email Reply System

This chapter documents the **Followup Agent**: a real-world productivity tool built with the OpenAI Agents SDK. It takes pasted email conversation threads and generates a professional, context-aware reply — no repetition, tone-matched, and concise. This project is a direct application of the manager-specialist pattern from `deep_research_my_version`.

---

## 1. The Core Insight: Why the First Implementation Was Wrong

The initial attempt at this agent had a critical flaw — it used **zero AI**. All "agents" were plain Python classes doing regex and string manipulation.

```python
# What the WRONG version looked like (no LLM, no SDK)
class ReplyPlannerAgent:
    def _paraphrase(self, text):
        return text.replace('please', 'kindly')  # This is NOT an AI agent
```

The correct approach uses the **OpenAI Agents SDK** with real LLM calls — every step is a `Runner.run()` under the hood, managed by a `ManagerAgent`.

---

## 2. The Architecture: 5-Agent Pipeline

The correct design mirrors `deep_research_my_version` exactly: a **ManagerAgent** as the orchestrator, with specialists mounted as tools and a final specialist receiving a **handoff**.

### The 5 Agents:

1. **ParserAgent** (Tool): Structures the raw conversation chronologically. Handles ANY format — no brittle regex needed. The LLM parses "On Mon, Alice wrote..." just as well as "From: Bob".
2. **AnalyzerAgent** (Tool): Extracts tone, intent, open questions, and — critically — what **NOT** to repeat.
3. **DraftWriterAgent** (`draft_writer_agent.py`): Composes the first draft, matching tone and staying concise. Uses DeepSeek model via OpenAI-compatible API. Has a module-level docstring documenting its purpose.
4. **QualityAgent** (Handoff Target): Final gatekeeper. Outputs ONLY the polished email — no commentary, no pipeline artifacts.
5. **ManagerAgent** (Orchestrator): Controls the entire flow with tools + handoff.

### Handoff vs. Tool: Know the Difference

| Pattern | Use When | SDK Method |
|---------|----------|------------|
| **Tool** | You need the result back to continue the workflow | `agent.as_tool()` |
| **Handoff** | The specialist takes over fully — you're done after this | `handoff(agent)` |

The QualityAgent is a **handoff** because the Manager has nothing left to do after sending off the draft. The output of QualityAgent is the final response.

---

## 3. The Manager Instructions: The Most Critical File

The `ManagerAgent`'s `instructions` string is the entire workflow specification. If this is wrong, the pipeline breaks. The key is an **explicit, numbered sequence**:

```python
MANAGER_INSTRUCTIONS = (
    "Follow exactly this sequence:\n"
    "1. Use the Parser tool to structure the raw conversation.\n"
    "2. Use the Analyzer tool on the parsed output to extract context.\n"
    "3. Use the DraftWriter tool to compose a reply using the analysis.\n"
    "4. Handoff to the QualityAgent for final polish.\n\n"
    "Do NOT write the email yourself. Use your tools and handoff."
)
```

> [!IMPORTANT]
> The final line — `"Do NOT write the email yourself. Use your tools and handoff."` — is essential. Without it, the ManagerAgent will often shortcut and write the email directly, skipping the entire specialist pipeline.

---

## 4. Agents-as-Tools Pattern (Recap)

Each specialist is mounted onto the Manager using `.as_tool()`. This transforms a full `Agent` object into a callable function that the Manager's LLM can invoke.

```python
manager_agent = Agent(
    name="ManagerAgent",
    instructions=MANAGER_INSTRUCTIONS,
    tools=[
        parser_agent.as_tool(
            tool_name="Parser",
            tool_description="Parses raw email threads into structured, chronological messages."
        ),
        analyzer_agent.as_tool(
            tool_name="Analyzer",
            tool_description="Analyzes conversation to extract tone, intent, and context."
        ),
        draft_writer_agent.as_tool(
            tool_name="DraftWriter",
            tool_description="Composes professional email drafts based on the analysis."
        ),
    ],
    handoffs=[handoff(quality_agent)],
    model=deepseek_model,
)
```

---

## 5. The Gradio UI: Streaming Event Handling

The UI mirrors `deep_research.py` exactly. The key is `Runner.run_streamed()` with an `async for` loop listening to event types.

```python
result = Runner.run_streamed(manager_agent, input_text)

async for event in result.stream_events():
    if isinstance(event, AgentUpdatedStreamEvent):
        # Agent handoff happened
        current_agent = event.new_agent.name
        yield f"🤝 Handed off to {current_agent}"

    elif isinstance(event, RunItemStreamEvent):
        item = event.item
        if isinstance(item, ToolCallItem):
            tool_name = getattr(item.raw_item, 'name', 'tool')
            yield f"🛠️ [{current_agent}] Calling: {tool_name}..."
        elif isinstance(item, MessageOutputItem):
            text = ItemHelpers.text_message_output(item)
            if current_agent == "QualityAgent" and "Subject:" in text:
                final_email = text  # Capture the polished output
```

### Capturing the Final Email

The final polished email arrives as a `MessageOutputItem` from the `QualityAgent`. The trick is to check: (1) which agent is currently active, and (2) whether the message text looks like an email (`"Subject:" in text`).

---

## 6. Running the Project

The entire project runs within the `uv` environment managed by `pyproject.toml` at the project root. **Never** call `python3` directly for this project.

```bash
# From the project root: agents/
uv run 2_openai/Followup\ Agent/followup_app.py
```

> [!TIP]
> The `.env` file lives at `projects/agents/.env` — the path is resolved **relative to the script location** using `Path(__file__).resolve().parent / ".." / ".." / ".env"`. All agent files follow this same pattern from `deep_research_my_version`.

---

## 7. Key Design Principles Learned

1. **LLMs replace heuristics.** Don't write regex to detect "tone." Ask the LLM. It's more accurate and handles edge cases.
2. **Quality gates via handoff.** The final agent in a pipeline should own the output format and be a handoff target, not a tool call.
3. **Manager instructions define the contract.** The manager instructions must be an explicit, numbered sequence. Vague instructions → agent shortcuts the pipeline.
4. **Tools return, handoffs transfer.** Tools give back control; handoffs hand it off permanently. Use each appropriately.
5. **`uv run` is the execution standard.** All scripts in this course project use `uv run` against the root `pyproject.toml`.

---

> [!CAUTION]
> **Don't over-engineer the parser.** The first instinct is to write a sophisticated regex parser for email headers. With an LLM, this is completely unnecessary. Passing raw conversation text to a `ParserAgent` with clear instructions gets better results than 100 lines of regex, and handles edge cases (chat threads, WhatsApp copypastes, Slack exports) automatically.
