# Chapter 1: Foundational Mechanics (The "Hard Way")

To master Agentic AI, you must first understand the "Manual Loop." Frameworks like the OpenAI Agents SDK or CrewAI are abstractions; this chapter strip away the magic to show you the raw engineering required to build an autonomous system from scratch.

> [!TIP]
> **Why learn the "Hard Way"?**
> When a framework fails, or when you need to squeeze out maximum performance/customization, you need to know how to handle the raw JSON tool calls and state accumulation yourself.

---

## 1. The Pro-Level Environment
Before building, your environment must be bulletproof. In an Agency setting, you'll often toggle between **DeepSeek** (cost-efficiency) and **OpenAI** (maximum reasoning).

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

# Pro-Tip: Use override=True to ensure .env changes take effect without restarting the kernel
load_dotenv(override=True)

def get_client(provider="deepseek"):
    if provider == "deepseek":
        return OpenAI(
            api_key=os.getenv("deepseek_api_key"),
            base_url="https://api.deepseek.com"
        )
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = get_client("deepseek")
```

---

## 2. The Manual Agent Loop
An agent is simply an LLM in a `while` loop that has access to a registry of functions. 

### A. Defining Tools (The JSON Schema)
The LLM doesn't "see" your Python code; it sees a JSON description of it.

```python
# The Python Function
def get_weather(location: str):
    """Get the current weather in a given location"""
    return f"The weather in {location} is 72°F and sunny."

# The JSON Schema (The "Contract")
weather_tool_schema = {
    "name": "get_weather",
    "description": "Get the current weather in a given location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}
        },
        "required": ["location"]
    }
}
```

### B. The Dispatcher: "Big IF" vs "Globals"
How do you actually run the function the LLM asked for? Use one of these two architectural patterns:

| Pattern | Logic | Best For |
| :--- | :--- | :--- |
| **The Big IF** | Explicitly check `if tool_name == "x":` | Production (Type-safe & Secure) |
| **The Globals** | `globals().get(tool_name)(**args)` | Rapid Prototyping (Clean but "Magic") |

#### Example: The "Globals" Dispatcher
```python
import json

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        # Dynamic lookup in the global namespace
        func = globals().get(name)
        if func:
            output = func(**args)
            results.append({
                "role": "tool",
                "content": json.dumps(output),
                "tool_call_id": tool_call.id
            })
    return results
```

---

## 3. The Parallel Evaluator Pattern (The "Judge")
In high-stakes Agency work, one LLM output isn't enough. You run several models in parallel and use a "Judge Agent" to select the winner.

```python
import asyncio

async def run_parallel_eval(prompt):
    # Running different model personalities or providers simultaneously
    tasks = [
        client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": f"Personality A: {prompt}"}]),
        client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": f"Personality B: {prompt}"}]),
    ]
    responses = await asyncio.gather(*tasks)
    
    # The Judge Agent selects the best response
    judge_prompt = f"Selection: {responses[0].choices[0].message.content} vs {responses[1].choices[0].message.content}"
    # ... logic to return winner
```

---

## 4. Case Study: Marriage Industry Agent
Building an agent loop from first principles to solve a complex commercial problem: **Conflict Resolution**.

### The Flow:
1. **System Prompt:** "You are a crisis mediator. Create a plan, execute steps, and provide a resolution."
2. **Tools:** `create_todos`, `mark_complete`, `get_todo_report`.
3. **Execution:** The agent doesn't just "talk"; it manages its own state using the todo tools until the "key issues" are resolved.

> [!IMPORTANT]
> **The Takeaway:**
> By forcing the agent to use a `todo` tool, we introduce **Chain of Thought (CoT)** reasoning into the UI. The user sees the agent "thinking" and "doing" before they see the final answer.

---

## 5. Gradio: Building a Stateful UI
Generic chat bubbles are for consumers. For Enterprises, you need **Stateful Dashboards** using `gr.Blocks`.

```python
import gradio as gr

with gr.Blocks() as demo:
    state = gr.State([]) # Persistent memory across interactions
    chatbot = gr.Chatbot()
    
    with gr.Row():
        input = gr.Textbox(placeholder="What is your research goal?")
        btn = gr.Button("Execute Agent")

    # In gr.Blocks, you have granular control over the data flow
    btn.click(agent_loop, inputs=[input, state], outputs=[chatbot, state])

---

### The Architecture of "Magic": Decorators
In Lab 5, we start seeing decorators like `@function_tool`.
- **What is a Decorator?** It's a **Wrapper**. Think of it as a "Sweetener" for your function. It "hugs" your code to give it extra powers without you writing the boilerplate.
- **The Translator Role:** Without decorators, you have to write painful JSON schemas manually (The "Hard Way"). The decorator acts as a **Translator**, automatically reading your docstrings and type hints to tell the LLM exactly how to use your code.
```

---

### Agency Pro-Tip: The "Zero Bullshit" Rule
Never allow an agent to report "internal knowledge" for time-sensitive tasks. Even in these foundational loops, force the agent to call a `search_tool` if the data is older than its training cutoff.
