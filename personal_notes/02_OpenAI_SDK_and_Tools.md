# Chapter 2: Professional Frameworks (OpenAI SDK)

Once you understand the manual mechanics, you'll find that building production-grade agents requires a framework that handles the boilerplate. The **OpenAI Agents SDK** is the "Goldilocks" choice: lightweight, Pythonic, and highly scalable.

---

## 1. The Core Components
The foundation of the SDK rests on three pillars:

| Component | Purpose | Analogy |
| :--- | :--- | :--- |
| **Agent** | Defines instructions and model configuration. | The Brain |
| **Runner** | Executes the agent loop and manages state. | The Heartbeat |
| **Tool** | Python functions wrapped for LLM use. | The Hands |

```python
from agents import Agent, Runner, function_tool

# Example: A simple Specialist Agent
researcher = Agent(
    name="Researcher",
    instructions="You are a data analyst. Find facts, not opinions.",
    model=deepseek_model
)
```

---

## 2. `@function_tool`: The "Hands" of the Agent
The `@function_tool` decorator is the most powerful utility in the SDK. It automatically converts Python docstrings and type hints into the JSON schema required by the LLM.

### Why Type Hinting is Mandatory:
The LLM uses your type hints (`str`, `int`, `list[str]`) to validate the arguments it generates.

```python
@function_tool
def fetch_stock_price(ticker: str):
    """
    Fetch the current stock price for a given ticker symbol.
    
    Args:
        ticker: The stock symbol (e.g., AAPL, TSLA)
    """
    # Logic to fetch price
    return {"ticker": ticker, "price": 150.00}
```

---

## 3. Handoffs: Transfer of Consciousness
In the manual loop, you had to write complex `if` statements to move between tasks. In the SDK, you use **Handoffs**.

> [!IMPORTANT]
> **Difference: Tool vs. Handoff**
> - **Tool:** The agent runs an errand and *returns* to its current task.
> - **Handoff:** The agent *transfers control* entirely to another specialized agent.

```python
# The Manager Agent can hand off to a Specialist
manager = Agent(
    name="Manager",
    handoffs=[researcher],
    instructions="Determine if the user needs research. If so, hand off to the Researcher."
)
```

---

## 4. The Bouncer Pattern (Guardrails)
To prevent hallucinations, jailbreaks, or expensive off-topic queries, we use **Guardrails**. This is the "Bouncer" that checks everyone at the door.

```python
from agents import input_guardrail, GuardrailFunctionOutput

@input_guardrail
async def block_competitors(ctx, agent, message):
    if "competitor_name" in message.lower():
        # Trigger a tripwire: the agent will never see this message
        return GuardrailFunctionOutput(tripwire_triggered=True)
    return GuardrailFunctionOutput(tripwire_triggered=False)

safe_agent = Agent(
    name="SafeAgent",
    input_guardrails=[block_competitors]
)
```

---

## 5. Structured Output with Pydantic
For agents that integrate with other software (CRMs, Databases, Apps), you cannot rely on free-flowing text. You must enforce **Structured Output**.

```python
class ContactLeads(BaseModel):
    names: list[str]
    emails: list[str]
    priority: int

sales_agent = Agent(
    name="SalesLeadGenerator",
    output_type=ContactLeads # The agent's final message MUST match this schema
)

> [!IMPORTANT]
> **Why Pydantic for Agency Work?**
> When integrating with external systems (CRMs, SQL Databases, Zapier), you cannot rely on "maybe" outputs. Pydantic ensures the LLM sends **valid JSON** that your other software can consume without crashing. It turns a "Probabilistic" LLM into a "Deterministic" system.
```

---

### Agency Pro-Tip: The "Trace" Utility
Always wrap your production runs in `trace()`. 
```python
with trace("Cold Outreach Campaign"):
    result = await Runner.run(manager, "Find 3 leads in SaaS and draft emails.")
```
This produces a detailed execution log (tokens, tool calls, latencies) that you can use to debug performance bottlenecks or justify billing to your clients.
