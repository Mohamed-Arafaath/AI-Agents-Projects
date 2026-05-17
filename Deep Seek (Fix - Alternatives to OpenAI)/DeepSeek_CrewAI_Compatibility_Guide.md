# DeepSeek & CrewAI: The Definitive Compatibility Guide

*A synthesized overview of the differences, errors, and custom architectural fixes required to make CrewAI work with DeepSeek models, compiled from our progression across multiple agentic projects.*

---

## Executive Summary

CrewAI is fundamentally optimized for the OpenAI ecosystem. Out of the box, it relies heavily on native OpenAI endpoints, structured JSON schemas (`response_format`), and highly reliable internal tool-call parsing. 

When replacing OpenAI with **DeepSeek (`deepseek-reasoner` / `deepseek-chat`)**, several native mechanisms break down. DeepSeek rejects forced structured schemas, fails to properly escape large JSON strings (leading to parsing loops), and aggressively returns markdown fences even when instructed not to. 

This guide consolidates all the battle-tested monkey-patches, architectural workarounds, and configuration shifts we've developed to make DeepSeek operate flawlessly at an enterprise level within CrewAI.

---

## 1. The Structured Output Bug (400 Bad Request)

### The Symptom
When hooking up DeepSeek directly through the `LLM` class or via `config.yaml`, the crew crashes immediately upon kickoff:
```
openai.BadRequestError: Error code: 400 - {'error': {'message': 'This response_format type is unavailable now', 'type': 'invalid_request_error'}}
```

### The Root Cause
CrewAI natively supports DeepSeek. However, its native integration relies on OpenAI's SDK using `client.beta.chat.completions.parse()`, which forcefully sends a structured `response_format` schema with every API call. **DeepSeek supports function calling but actively rejects structured output schemas.**

### The Fix
You must force CrewAI to use **LiteLLM** instead of its native provider for DeepSeek. LiteLLM gracefully degrades the request and handles DeepSeek's limitations correctly.

**Option A (String Passthrough - Preferred):**
In `crew.py`, extract the model string out of the config so CrewAI passes it directly as a string, invoking standard inference instead of structured inference:
```python
config = self.agents_config['my_agent'].copy()
if 'model' in config:
    config['llm'] = config.pop('model')  # e.g., "deepseek/deepseek-chat"
```

**Option B (Explicit LiteLLM Flag):**
```python
from crewai import LLM
planning_llm = LLM(model="deepseek/deepseek-chat", is_litellm=True)
```
*(Note: Requires `uv add 'crewai[litellm]'`)*

---

## 2. The JSON Tool-Calling Bug (`code_interpreter` Timeout Loops)

### The Symptom
When an agent is assigned `allow_code_execution=True` to write and test code, the run eventually crashes after 10 minutes (wall-clock limit) with a repetitive log trace:
```
Error: Failed to parse tool arguments as JSON:
Unterminated string starting at: line 1 column 62...
```

### The Root Cause
CrewAI's default `code_interpreter` forces the agent to pack its generated Python script into a JSON string (`{"code": "print('hello')..."}`). While GPT-4o handles string escaping perfectly, **DeepSeek V3 and R1 frequently fail to escape newlines (`\n`), single quotes, and double quotes in scripts longer than 100 lines.** This results in malformed JSON, triggering an infinite retry loop until the system times out.

### The Fix: Belt-and-Suspenders Architecture
Never use `allow_code_execution=True` directly with DeepSeek for complex logic. Use a dual-layer fix:

**Layer 1: The `SafeCodeExecutorTool`**
Bypass JSON serialization entirely by forcing the flow through the filesystem. Create a custom tool that uses Pydantic to capture the raw string, write it to a temporary `.py` file, and sub-process it.
```python
tools=[SafeCodeExecutorTool()] # Instead of allow_code_execution=True
```

**Layer 2: The Regex Monkey-Patch**
Because DeepSeek can sometimes fail to even format the outer `{}` JSON wrapper of the tool call, we monkey-patch `crewai.utilities.agent_utils.parse_tool_call_args` to fall back on regex extraction when standard `json.loads` fails.
```python
def _patched_parse_tool_call_args(func_args, func_name, call_id, original_tool=None):
    if isinstance(func_args, str) and func_name in ["code_interpreter", "safe_code_executor"]:
        try:
            return json.loads(func_args), None
        except json.JSONDecodeError:
            match = re.search(r'(?:"code"|\'code\')\s*:\s*["\'](.*)["\']\s*}?\s*$', func_args, re.DOTALL)
            if match:
                code_content = match.group(1).replace('\\n', '\n')
                return {"code": code_content}, None
    return _original_parse(func_args, func_name, call_id, original_tool)
```

---

## 3. Persistent Memory Failures (LanceDB)

### The Symptom
Enabling `memory=True` in the Crew configuration causes crashes during vector storage / retrieval operations. If the run completes, subsequent runs may behave erratically or output "intent text" (e.g. "I will perform research").

### The Root Cause
CrewAI's memory extractor attempts to use OpenAI-style function calling schemas to distill memories. DeepSeek fails this parsing layer. Consequently, failed payloads get saved into the LanceDB vector store with high score confidences (0.94+) as "poisoned memories."

### The Fix: `_PlainJsonLLM` Wrapper
Wrap your memory LLM object in a class that explicitly disables function calling, forcing CrewAI's `analyze.py` to revert to parsing raw text.

```python
class _PlainJsonLLM:
    def __init__(self, llm): self.llm = llm
    def supports_function_calling(self) -> bool: return False  # Force plain-text path
    def call(self, messages): return self.llm.call(messages)
    # ... proxy other methods
```
*Note: If poisoned memory has already accumulated, you must `rm -rf memory/` before rerunning.*

---

## 4. The Hidden `planning=True` Bottleneck

### The Symptom
Adding `planning=True` to the `Crew()` instantiation causes an instant crash requiring an `OPENAI_API_KEY`, or causes agents to hallucinate intentions ("I will use a tool...") rather than actually attempting tasks.

### The Root Cause
CrewAI spins up an internal, invisible `PlanningAgent` if `planning=True` is enabled. If not supplied an LLM, it defaults to OpenAI. Furthermore, DeepSeek's outputs to meta-planning prompts often generate "ReAct" style thought processes demanding nonexistent tools.

### The Fix
**Do not use `planning=True` with DeepSeek.** Instead, make "Planning" a legitimate, visible task in the sequential pipeline:
1. `planning_task` (Agent: `architecture_planner` using `deepseek-reasoner`)
2. `coding_task` (Agent: `backend_coder` taking `context: [planning_task]`)

---

## 5. Markdown Fencing Contamination

### The Symptom
Despite stern prompt instructions ("Output ONLY raw python code, absolutely no markdown borders"), output files invariably render with formatting:
```python
```python
import sys
# ...
```
```

### The Root Cause
DeepSeek’s alignment heavily leans toward Markdown formatting for code blocks. Prompt engineering cannot reliably overcome this intrinsic behavioral bias over a multi-iteration task execution.

### The Fix
Implement a strict post-processing phase in `main.py` immediately after `kickoff()`. Do not rely on the LLM to format its deliverables perfectly.
```python
import re, glob
# Clean compiled python files
for py_file in glob.glob("output/*.py"):
    with open(py_file, "r") as f:
        cleaned = re.sub(r'^```[a-zA-Z]*\n', '', f.read().strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r'\n```$', '', cleaned)
    with open(py_file, "w") as f:
        f.write(cleaned)
```

---

## 6. Model Workload Distribution (R1 vs V3)

DeepSeek offers two primary endpoints. OpenAI defaults to a universal unified model (GPT-4o), but optimizing DeepSeek requires deliberate separation of concerns based on the token generation speed and "thinking" capacity.

| Role | Preferred Model | Why |
| :--- | :--- | :--- |
| **Architect / Planner** | `deepseek-reasoner` (R1) | Complex architecture design, edge-case coverage, and logical mapping require deep Chain of Thought (CoT). |
| **Code Reviewer / QA**| `deepseek-reasoner` (R1) | Bug finding and logic fixing require careful, deliberate reasoning. |
| **Coder / Test Writer** | `deepseek-chat` (V3)   | Synthesizing code from a perfected blueprint is relatively simple for an LLM. It favors speed and lower context costs. |

---

## Conclusion

Adapting CrewAI to DeepSeek transforms it from a framework dependent on OpenAI's proprietary syntax handlers into a truly model-agnostic, resilient system. 

By pushing code execution to the raw filesystem (`SafeCodeExecutorTool`), forcing schema parsing into plain text via wrappers (`_PlainJsonLLM`), and explicitly routing deep reasoning tasks vs. fast execution tasks to different models, we achieve a highly stable, production-grade autonomous agent pipeline capable of zero-shot complex enterprise problem solving.
