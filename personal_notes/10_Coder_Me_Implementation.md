# Chapter 10: CoderMe — Autonomous Code Generation & Self-Verification Pipeline

The **CoderMe** project is an industry-standard autonomous coding crew. Unlike the template "Researcher + Reporter" boilerplate, this crew **writes, executes, debugs, and self-verifies Python code** given any coding assignment. It uses persistent memory so errors from previous runs are never repeated — the agent only improvises.

---

## 1. The Core Insight: Why "Write-Only" Coding Agents Fail

Most AI coding agents have a fatal flaw: they **generate code but never run it**. This leads to:
- Syntax errors that could be caught in 0.1 seconds
- Logic bugs that look correct on paper but fail at runtime
- Missing imports that the LLM "assumed" were available

### The Solution: The "Write → Execute → Verify" Loop
CoderMe enforces a strict contract: **no code is accepted unless it has been executed and proven to work**. Both the `senior_coder` and `code_reviewer` agents have `allow_code_execution=True`, meaning they can run Python in a sandbox to verify their output.

> [!IMPORTANT]
> **`allow_code_execution=True`** is the single most impactful setting for coding agents. Without it, you're trusting an LLM to write perfect code on the first try — which it won't.

---

## 2. The 3-Agent Sequential Pipeline

CoderMe uses a strict **Plan → Code → Review** sequential process. Unlike StockPickerMe's hierarchical architecture, this is intentionally linear because each step depends entirely on the previous one's output.

| Agent | Role | Tools | Key Features |
| :--- | :--- | :--- | :--- |
| **code_planner** | Software Architect | None | Designs the blueprint — no code written |
| **senior_coder** | Python Engineer | Built-in code execution | Writes AND executes code until it passes |
| **code_reviewer** | QA Engineer | Built-in code execution | Reviews, re-executes, writes `review_report.txt` |

### Why Sequential Over Hierarchical?
```
code_planner → senior_coder → code_reviewer
     ↓              ↓              ↓
  (plan)    (needs the plan)  (needs the code)
```
Each step **depends on the previous one's output**. There's nothing to parallelize:
- Coder can't write code without the plan
- Reviewer can't review code that doesn't exist yet

A hierarchical process would just add a 4th agent (manager) burning tokens for no benefit. Sequential is the industry standard for linear pipelines.

---

## 3. Implementation Step 1: Agent Configuration (`agents.yaml`)

Each agent uses the `{assignment}` variable and `deepseek/deepseek-chat` as the model.

```yaml
code_planner:
  role: >
    Senior Software Architect & Technical Planner
  goal: >
    Analyze the given coding assignment: "{assignment}" and produce a crystal-clear,
    step-by-step technical design plan.
  backstory: >
    You are a battle-hardened software architect with 15 years of experience...
  model: deepseek/deepseek-chat

senior_coder:
  goal: >
    Write clean, production-grade Python code to solve: "{assignment}".
    Use the code execution tool to VERIFY your solution actually runs before submitting it.
  # ↑ The backstory explicitly instructs the agent to EXECUTE and DEBUG

code_reviewer:
  goal: >
    Review the Python code produced for: "{assignment}".
    Execute the code to verify it runs correctly and passes all edge cases.
```

> [!TIP]
> **Key Prompt Engineering Insight:** Notice how both the coder and reviewer backstories explicitly say "You ALWAYS test your code by executing it." This is critical — if you don't tell the agent to use its tools, it often won't. The backstory acts as a persistent system prompt that reinforces tool usage.

---

## 4. Implementation Step 2: Task Architecture (`tasks.yaml`)

### The Planning Task — Blueprint Only
```yaml
planning_task:
  description: >
    Analyze the following coding assignment and create a detailed technical plan:
    ASSIGNMENT: {assignment}
    Your plan must include:
    1. Problem breakdown
    2. Required imports and dependencies
    3. Function signatures with types
    4. Edge cases and error handling
    5. Implementation order
    7. Test cases (inputs → expected outputs)   # ← Forces concrete pass/fail criteria
    Do NOT write any actual Python code — only the blueprint.
  agent: code_planner
```

> [!TIP]
> **Why the plan includes test cases:** By forcing the planner to define test cases (input → expected output), the coder has a concrete checklist to verify against. Without this, the coder would "test" by running once and assuming it works.

### The Coding Task — Write + Execute
```yaml
coding_task:
  description: >
    ...
    - EXECUTE your code using the code execution tool to verify it works
    - If execution fails, debug and fix until it passes
    - The code MUST be verified-as-working before you submit it
  agent: senior_coder
```

### The Review Task — Triple Output
```yaml
review_task:
  description: >
    ...
    You MUST create exactly 3 output files using the File Writer tool:
    1. output/solution.py — The complete, final Python code ONLY
    2. output/output.txt — The actual stdout from executing the code
    3. output/errors.txt — Review log (issues found, fixes applied, warnings)
  agent: code_reviewer
```

> [!IMPORTANT]
> **Why 3 separate files?** In professional agency work, separating code from output from errors creates an auditable "Paper Trail." Clients can verify the code works by checking `output.txt`, and debug issues by checking `errors.txt`, without digging through the raw code.

---

## 5. Implementation Step 3: The `crew.py` Agent Definitions

### The "Model" Key Bridge (DeepSeek Compatibility)
Same pattern as StockPickerMe — YAML uses `model:` but CrewAI expects `llm:`. Use the **string passthrough** pattern, NOT `LLM(model=..., is_litellm=True)` wrapper:

```python
@agent
def senior_coder(self) -> Agent:
    config = self.agents_config['senior_coder'].copy()
    if 'model' in config:
        config['llm'] = config.pop('model')  # Bridge YAML → CrewAI (string passthrough)
    return Agent(
        config=config,
        # NO tools — agents use built-in code execution only.
        # Adding tools to DeepSeek agents causes ReAct format failures.
        allow_code_execution=True,    # ← Built-in code runner
        code_execution_mode="unsafe", # ← Direct host execution (no Docker)
        max_iter=10,                  # Enough retries to debug
        max_retry_limit=3,            # Task-level error retries
        max_execution_time=600,       # 10 min hard timeout
        allow_delegation=False,       # Stays in its lane
        verbose=True,
    )
```

> [!IMPORTANT]
> **Do NOT pass `tools=[FileReadTool(), FileWriterTool()]`** to agents. DeepSeek fails at ReAct tool-call format, causing agents to output intent text ("I'll search for...") instead of actual code. The built-in `allow_code_execution=True` is all they need.

### Agent Safeguard Parameters

| Parameter | Planner | Coder | Reviewer | Purpose |
| :--- | :---: | :---: | :---: | :--- |
| `max_iter` | 5 | 10 | 10 | Max tool-call iterations before forced stop |
| `max_execution_time` | 300s (5m) | 600s (10m) | 480s (8m) | Hard wall-clock timeout |
| `max_retry_limit` | — | 3 | 2 | Task-level retries on errors |
| `allow_code_execution` | ❌ | ✅ | ✅ | Built-in code runner (no Docker) |
| `code_execution_mode` | — | `"unsafe"` | `"unsafe"` | Direct host execution |
| `tools` | none | none | none | No external tools — DeepSeek fails at ReAct |
| `allow_delegation` | ❌ | ❌ | ❌ | Keeps agent in its own lane |

> [!IMPORTANT]
> **`max_iter` vs. `max_execution_time` — Use Both (Belt-and-Suspenders):**
> - **`max_iter`**: Limits the number of iterations (thinking + tool calls). Prevents infinite loops.
> - **`max_execution_time`**: Wall-clock timeout in seconds. Catches scenarios where a single tool call hangs forever (e.g., code that runs `while True`).
> - **`max_retry_limit`**: How many times CrewAI retries the *entire task* if the agent fails to produce valid output. Different from `max_iter` which limits *within* a single task attempt.

---

## 6. Persistent Memory: Never Repeat the Same Mistake

This is what makes CoderMe elite. The crew has **persistent memory** stored in `./memory/`, meaning:

| Memory Type | What It Does |
| :--- | :--- |
| **Short-term** | Context flows between planner → coder → reviewer within a single run |
| **Long-term** | Errors, solutions, and patterns persist across ALL runs |
| **Entity** | Tracks specific entities (function names, error types) for precise recall |

### How It Works Across Runs
```
Run 1: Assignment → coder writes buggy code → reviewer catches errors → all stored in ./memory/
Run 2: Same/similar assignment → Memory recalls past errors → coder avoids them → only improvises
Run 3: Different assignment → Memory recalls patterns ("always add edge cases") → better code from start
```

### The Memory Configuration (Ported from StockPickerMe)
```python
from crewai.memory import Memory

memory = Memory(
    llm=_PlainJsonLLM("deepseek/deepseek-chat"),  # No 400 errors (DeepSeek compat)
    embedder=_hash_embedder,                        # No 429 errors (zero API calls)
    storage="./memory",                             # Local LanceDB persistence
)

Crew(
    memory=memory,
    tracing=False,   # Suppresses crew_memory serialization warning
)
```

> [!TIP]
> **Memory is what separates a toy from a professional tool.** Without it, you're paying for the same mistakes every single run. With it, the crew gets smarter over time — like training a human developer who remembers their code reviews.

### Memory Infrastructure (Zero External API Dependency)
Both components are ported directly from StockPickerMe's battle-tested implementation:

- **`_PlainJsonLLM`** — Wraps DeepSeek in plain-text mode. DeepSeek rejects `response_format` schemas (400 error), so this wrapper returns `supports_function_calling() → False`, forcing CrewAI's `analyze.py` to use the plain-text JSON parsing branch.

- **`_hash_embedder`** — SHA256-based deterministic vectors (3072 dimensions). No embedding API calls needed. Trade-off: exact-match only (not semantic), but sufficient for persisting task outputs and error patterns.

> [!WARNING]
> **Known Warnings (Safe to Ignore):**
> - `Memory extraction failed, storing full content` — DeepSeek sometimes returns prose instead of JSON. CrewAI falls back to storing the entire content as one memory. Still persisted.
> - `extra_forbidden: tools_mentioned` — DeepSeek is smarter than expected and adds extra fields. CrewAI's Pydantic model rejects them. Core memory still saved.
> - `Invalid type Memory for attribute 'crew_memory'` — OpenTelemetry can't serialize the Memory object. Fixed by `tracing=False`. Zero impact.

---

## 7. The `main.py` Entry Point

The entry point generates a dynamic query slug from the assignment text. This ensures that every coding task execution is stored securely in its own unique subfolder and doesn't overwrite past runs.

```python
def run():
    default_assignment = (
        'Write a python program to calculate the first 10,000 terms of this series, '
        'multiplying the total by 4: 1 - 1/3 + 1/5 - 1/7 + ... + ...'
    )
    assignment = os.environ.get("ASSIGNMENT", default_assignment)

    # Build query-specific output subfolder: output/<slug>/
    slug = _slugify(assignment)
    output_dir = Path("output") / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = {
        "assignment": assignment,
        "output_dir": str(output_dir),
    }

    CoderMe().crew().kickoff(inputs=inputs)
```

### Input Variables
Two main variables:
- `{assignment}` — the coding task to solve. Passed via the `ASSIGNMENT` env variable.
- `{output_dir}` — the dynamically generated output path so tasks save to `output/<query_slug>/`.

### Running the Crew
You can define a custom task by passing the `ASSIGNMENT` variable:
```bash
# From the coder_me project root
ASSIGNMENT="Build a flask app for task management" uv run coder_me

# Or run the default Pi calculation sequence:
uv run coder_me
```

> [!TIP]
> **Production Standard:** Never use `python3 src/main.py`. Always use the entry point defined in `pyproject.toml`:
> ```bash
> uv run coder_me
> ```
> This ensures all environment variables and internal package references are resolved correctly.

---

## 8. Output Architecture

The crew produces 2 files written via `output_file:` in `tasks.yaml`. They are stored dynamically inside a generated `output/<query_slug>/` folder to prevent overwriting past runs:

| File | Written By | Contents | Purpose |
| :--- | :--- | :--- | :--- |
| `output/<slug>/solution.py` | `senior_coder` (via `output_file:`) | Raw, runnable Python code | The deliverable |
| `output/<slug>/review_report.txt` | `code_reviewer` (via `output_file:`) | Execution stdout + review findings + fixes | Audit trail |

> [!IMPORTANT]
> **Files are written via `output_file:` in `tasks.yaml`**, not via FileWriterTool. This is the correct CrewAI pattern — the task output is automatically saved to the specified path. No tool calls needed.

> [!TIP]
> **Why the reviewer writes `review_report.txt` (not the coder):** The coder's job is to write the best code it can. The reviewer's job is to verify it meets production standards. Separating the two outputs creates an auditable trail — code in `solution.py`, verdict in `review_report.txt`.

---

## 9. The `.env` Loading Pattern

Same shared-root pattern as all crews in `3_crew/`:

```python
_PROJECT_ROOT = Path(__file__).resolve().parents[4]  # up to /agents/
_ENV_PATH = _PROJECT_ROOT / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH, override=True)
```

This means all crews (`stock_picker_me`, `startup_analyzer_me`, `coder_me`) share the same `.env` file at the `/agents/` root, containing:
- `DEEPSEEK_API_KEY`
- `SERPER_API_KEY` (not needed for coder_me, but available)
- `PUSHOVER_*` keys (not needed for coder_me)

---

## 10. Crew-Level Planning — ⚠️ DO NOT USE with DeepSeek Coding Crews

```python
# ❌ WRONG — breaks DeepSeek coding agents
Crew(
    planning=True,
    planning_llm=LLM(model="deepseek/deepseek-chat", is_litellm=True),
)

# ✅ CORRECT — planning_task handles the blueprint already
Crew(
    # planning=True NOT set
    memory=memory,
    tracing=False,
)
```

`planning=True` makes CrewAI generate a meta-plan **in addition to** `planning_task`. This meta-plan adds steps like "search for existing implementations" and "read previous files" — but DeepSeek agents have no search/read tools, so they output intent text ("I'll search for...") instead of code, and return that as their final answer.

> [!CAUTION]
> **`planning=True` is the single biggest cause of "intent text" outputs.** The `planning_task` already handles architecture design. Using `planning=True` on top creates a second meta-layer that agents cannot execute, causing them to return "I'll start by searching..." as their final answer.

---

## 11. Full Project Structure

```
coder_me/
├── pyproject.toml              # Dependencies: crewai[tools], python-dotenv
├── src/coder_me/
│   ├── __init__.py
│   ├── main.py                 # Entry point — passes {assignment} to crew
│   ├── crew.py                 # 3 agents, 3 tasks, memory, sequential process
│   ├── config/
│   │   ├── agents.yaml         # code_planner, senior_coder, code_reviewer
│   │   └── tasks.yaml          # planning_task, coding_task, review_task
│   └── tools/
│       ├── __init__.py
│       └── custom_tool.py      # Template (unused — tools come from crewai_tools)
├── knowledge/
│   └── user_preference.txt     # Knowledge source (optional)
├── output/                     # Created at runtime
│   └── <query_slug>/           # Dynamic subfolder based on the ASSIGNMENT
│       ├── solution.py         # Final code
│       └── review_report.txt   # Review log & execution stdout
└── memory/                     # Persistent LanceDB storage (auto-created)
```

---

## 12. Key Design Principles Learned

1. **"Write-Only" agents are useless.** `allow_code_execution=True` is non-negotiable for coding crews.
2. **Test cases belong in the plan.** If the planner doesn't define concrete pass/fail criteria, the coder has nothing to verify against.
3. **Belt-and-suspenders safeguards.** Always use BOTH `max_iter` (iteration cap) AND `max_execution_time` (wall-clock timeout). One catches loops, the other catches hangs.
4. **Memory is the moat.** Without persistent memory, you pay for the same mistakes every run. With it, the crew accumulates institutional knowledge.
5. **Sequential is correct for linear pipelines.** Don't use hierarchical just because it sounds fancier — it adds a manager agent that burns tokens for no benefit when the flow is A → B → C.
6. **Separate code from output from errors.** Three output files create an auditable paper trail that clients can verify independently.
7. **Backstories enforce tool usage.** If you don't explicitly tell the agent "ALWAYS run the code yourself," it often won't use `allow_code_execution` even when it's enabled.
8. **`allow_delegation=False` keeps agents focused.** Without it, agents can pass work to each other, creating unpredictable chains and wasted tokens.

---

## 13. First-Run Debugging Saga — All Errors & Fixes

This section documents every error hit during the **first real execution** of CoderMe (`uv run coder_me`), why each happened, and the exact fix applied.

---

### 13.1 Error #1 — Docker Not Installed

**Error:**
```
RuntimeError: Docker is not installed. Please install Docker to use code execution
with agent: Senior Python Engineer
```

**Root Cause:**
`allow_code_execution=True` defaults to `code_execution_mode="docker"`. CrewAI tries to sandbox code in a Docker container. If Docker isn't installed, it throws a `RuntimeError` immediately at agent initialization — before any LLM call is even made.

**Why it's misleading:** The error suggests you MUST install Docker to use code execution. That's wrong — there's an alternative.

**The Fix — `code_execution_mode="unsafe"`:**
```python
return Agent(
    config=config,
    allow_code_execution=True,
    code_execution_mode="unsafe",  # ← runs on host machine, no Docker needed
)
```

| Mode | Requires | Isolation |
| :--- | :--- | :--- |
| `"docker"` (default) | Docker installed | ✅ Fully sandboxed container |
| `"unsafe"` | Nothing | ⚠️ Runs directly on your Mac |

> [!WARNING]
> `"unsafe"` means the agent's generated code runs directly on your machine with no sandbox. Only use this for trusted assignments. For production, install Docker and use `"docker"` mode.

---

### 13.2 Error #2 — Docker Validation Bug (CrewAI v1.12.x)

**Error:**
```
RuntimeError: Docker is not installed. Please install Docker to use code execution
with agent: Senior Python Engineer
```
*(Same error even after adding `code_execution_mode="unsafe"`)*

**Root Cause:**
CrewAI v1.12.x has a bug in `crewai/agent/core.py`. The method `_validate_docker_installation()` is called at line 297 in `post_init_setup` **before** the code checks whether `code_execution_mode` is `"unsafe"` or `"docker"`. So even with `code_execution_mode="unsafe"`, the Docker check fires first and throws.

**The Fix — Monkey-Patch the Validation Method:**
```python
# Confirmed: class Agent(BaseAgent) in crewai/agent/core.py line 126
def _noop_docker_check(self) -> None:
    """Skip Docker validation — unsafe mode runs directly on the host."""
    pass

import crewai.agent.core as _crewai_core
_crewai_core.Agent._validate_docker_installation = _noop_docker_check
```

This replaces the validation method with a no-op **at module load time**, before any agent is instantiated. The `code_execution_mode="unsafe"` then works as intended.

> [!TIP]
> **Monkey-patching rule:** Always confirm the exact class name from source before patching. We ran `grep -n "class.*Agent"` on `core.py` and confirmed it's `class Agent(BaseAgent)` at line 126 — NOT `CrewAgent` or any other name.

---

### 13.3 Error #3 — `planning=True` Uses OpenAI by Default

**Error:**
```
ImportError: Error importing native provider: OPENAI_API_KEY is required
```

**Root Cause:**
`planning=True` in the Crew constructor makes CrewAI create a hidden internal **PlanningAgent** before any task runs. This agent is created in `crewai/utilities/planning_handler.py` with **no model specified** — so it defaults to OpenAI. Since we don't have an OpenAI key (only DeepSeek), it fails immediately.

**The Fix — `planning_llm`:**
```python
Crew(
    planning=True,
    planning_llm=LLM(model="deepseek/deepseek-chat", is_litellm=True),  # ← explicit model
)
```

> [!IMPORTANT]
> **Rule:** Any time you use `planning=True`, you MUST also set `planning_llm` explicitly. Otherwise CrewAI defaults to OpenAI — even if all your agents are configured with DeepSeek.

---

### 13.4 Error #4 — DeepSeek `response_format` Rejection (400)

**Error:**
```
openai.BadRequestError: Error code: 400 - {'error': {'message': 'This response_format
type is unavailable now', 'type': 'invalid_request_error'}}
```

**Root Cause:**
CrewAI v1.12.x added DeepSeek as a **native provider** (line 314 of `crewai/llm.py`). Native providers use `client.beta.chat.completions.parse()` which sends a structured `response_format` JSON schema with every request. **DeepSeek's API claims to support function calling but rejects structured output schemas** — a known DeepSeek limitation first documented in the StockPickerMe notes (Section 9.3).

The call chain:
```
crew_agent_executor.py → get_llm_response()
    → llm.call()
        → openai/completion.py → _handle_completion()
            → client.beta.chat.completions.parse(response_format=...) ← 400 HERE
```

**The Fix — Force LiteLLM Backend:**
```python
from crewai import LLM

# OLD (uses native DeepSeek provider → beta.parse() → 400):
config['llm'] = config.pop('model')  # just a string "deepseek/deepseek-chat"

# NEW (forces LiteLLM which handles DeepSeek correctly):
model_str = config.pop('model', 'deepseek/deepseek-chat')
config['llm'] = LLM(model=model_str, is_litellm=True)
```

The `is_litellm=True` flag is checked at `llm.py` line 407:
```python
if native_class and not is_litellm and provider in SUPPORTED_NATIVE_PROVIDERS:
    # use native (broken for DeepSeek)
else:
    # FALLBACK to LiteLLM ← this is what we want
```

Applied to **all 4 LLM consumers**: `code_planner`, `senior_coder`, `code_reviewer`, and `planning_llm`.

---

### 13.5 Error #5 — LiteLLM Package Not Installed

**Error:**
```
ImportError: Unable to initialize LLM with model 'deepseek/deepseek-chat'.
The LiteLLM fallback package is not installed.

To fix this, either:
  1. Install LiteLLM for broad model support: uv add 'crewai[litellm]'
```

**Root Cause:**
`is_litellm=True` requires the `litellm` package to be installed. While `stock_picker_me` already had it (added during its own setup), `coder_me` is a fresh project with a separate virtual environment that didn't have it.

**The Fix — One Command:**
```bash
uv add 'crewai[litellm]'
```

This installs:
- `litellm==1.82.6`
- `fastuuid==0.14.0` (dependency)
- Rebuilds the package

> [!TIP]
> **Always install `crewai[litellm]`** for any project using non-OpenAI/Anthropic models. DeepSeek, Ollama, OpenRouter — they all work through LiteLLM. The native providers only reliably support OpenAI and Anthropic.

---

### 13.6 Summary: Full Debug Session Fix Table

| Error | Root Cause | Fix |
| :--- | :--- | :--- |
| `Docker is not installed` | `allow_code_execution=True` defaults to Docker mode | Add `code_execution_mode="unsafe"` |
| `Docker is not installed` (persists) | CrewAI v1.12.x validates Docker before checking mode | Monkey-patch `_validate_docker_installation` to no-op |
| `OPENAI_API_KEY is required` | `planning=True` creates internal agent defaulting to OpenAI | Add `planning_llm=LLM(model=..., is_litellm=True)` |
| `response_format 400` | DeepSeek registered as native provider → uses `beta.parse()` | Use `LLM(model=..., is_litellm=True)` for all agents |
| `LiteLLM fallback not installed` | Fresh venv missing litellm package | `uv add 'crewai[litellm]'` |

### 13.7 Final Working `crew.py` Pattern for DeepSeek

```python
from crewai import Agent, Crew, Process, Task

# Monkey-patch: fixes Docker check bug in CrewAI v1.12.x
def _noop_docker_check(self) -> None:
    pass
import crewai.agent.core as _crewai_core
_crewai_core.Agent._validate_docker_installation = _noop_docker_check

# All agents: string passthrough (NOT LLM wrapper — string avoids 400 errors too)
config = self.agents_config['senior_coder'].copy()
if 'model' in config:
    config['llm'] = config.pop('model')  # string: "deepseek/deepseek-chat"

return Agent(
    config=config,
    # NO tools — DeepSeek fails at ReAct format when tools present
    allow_code_execution=True,
    code_execution_mode="unsafe",   # no Docker required
    ...
)

# Crew: NO planning=True, add tracing=False
Crew(
    agents=self.agents,
    tasks=self.tasks,
    process=Process.sequential,
    verbose=True,
    memory=memory,
    tracing=False,   # prevents Memory serialization errors
    # planning=True ← DO NOT ADD — breaks DeepSeek agent outputs
)
```

> [!IMPORTANT]
> **Two key changes from the "debugging session" fix table above:**
> 1. No `LLM(model=..., is_litellm=True)` wrapper — the string passthrough `config.pop('model')` also avoids the 400 error and is simpler.
> 2. No `planning=True` — see §10 above. The `planning_task` is the plan.

---

## 14. First-Run Quality Issues & Fixes

After all startup errors were resolved, the crew completed its first full run — but with a **quality problem**: the output files were never created.

### 14.1 The Symptom

The reviewer's final answer was:
```
"I'll start by reading the technical plan and any existing code to understand what needs to be reviewed."
```

And `ls output/` showed: **No output files found.**

The reviewer **said what it was going to do** instead of actually doing it. This is a classic `max_iter` exhaustion pattern in CrewAI — when an agent runs out of iterations, it returns its last "thought" as the final answer.

### 14.2 Root Cause 1 — No Explicit Context Chaining

In CrewAI sequential process, context *should* auto-pass between tasks — but it's unreliable, especially with LiteLLM. The reviewer was starting with an empty context and spending all its iterations just trying to figure out what code to review.

**Fix — explicit `context:` fields in `tasks.yaml`:**
```yaml
coding_task:
  agent: senior_coder
  context:
    - planning_task  # receives the blueprint from code_planner

review_task:
  agent: code_reviewer
  context:
    - planning_task  # original blueprint for reference
    - coding_task    # the code produced by senior_coder to review
```

> [!IMPORTANT]
> **Always set `context:` explicitly on tasks that depend on previous tasks.** Don't rely on sequential auto-passing — it's undocumented behaviour that can fail silently. Explicit context = the agent immediately has what it needs and can start working on iteration 1, not iteration 5.

### 14.3 Root Cause 2 — `max_iter=8` Too Low for Reviewer

The reviewer must do many steps in sequence:

| Step | Iterations Used |
|:---|:---:|
| Read/understand code from context | 1 |
| Execute code to check it works | 1 |
| Identify issues + apply fixes | 2–4 |
| Write `output/solution.py` | 1 |
| Write `output/output.txt` | 1 |
| Write `output/errors.txt` | 1 |
| **Minimum total** | **7–10** |

With `max_iter=8`, the reviewer was hitting the wall before it could write any files.

**Fix:**
```python
# crew.py — code_reviewer agent
max_iter=15,   # was 8 — reviewer needs room to read+execute+fix+write 3 files
```

### 14.4 Important Design Clarification — Output Files Are Deliverables, NOT Inputs

A common confusion: "won't the output/errors.txt file be reviewed?"

**No — and that's correct by design.** The 3 output files are the reviewer's **deliverable**, not its input.

```
Review flow (within one run):
1.  Reviewer READS code    ← via context: [coding_task]
2.  Reviewer THINKS        ← "Is it correct? Any bugs? PEP8?"
3.  Reviewer EXECUTES code ← sees real stdout / stderr
4.  Reviewer WRITES output/solution.py   ← FileWriterTool
5.  Reviewer WRITES output/output.txt    ← FileWriterTool
6.  Reviewer WRITES output/errors.txt    ← FileWriterTool
```

The output files are created at step 4–6 — after the review has already happened in the agent's reasoning.

**What about across runs?** The `./memory/` system handles this:
- Within a run → reviewer gets code via `context: [coding_task]`
- Across runs → persistent LanceDB memory recalls past errors automatically

> [!TIP]
> If you want the reviewer to explicitly read the previous run's `output/errors.txt` on the next run, you can add a `FileReadTool` instruction in the `review_task` description. But memory is the better mechanism — it's semantic and works across different assignments.

### 14.5 Updated Agent Parameters Table

| Parameter | Planner | Coder | Reviewer | Notes |
|:---|:---:|:---:|:---:|:---|
| `max_iter` | 5 | 10 | **10** | Reviewer: 10 iterations sufficient with no tools |
| `max_execution_time` | 300s | 600s | 480s | Unchanged |
| `max_retry_limit` | — | 3 | 2 | Unchanged |
| `allow_code_execution` | ❌ | ✅ | ✅ | Built-in code execution |
| `code_execution_mode` | — | `"unsafe"` | `"unsafe"` | Direct host execution |
| `tools` | none | **none** | **none** | Removed — DeepSeek ReAct failures |
| `context:` in task | — | `[planning_task]` | `[planning_task, coding_task]` | Explicit chaining |

---

## 15. The Root Cause Fix — "Intent Text" Problem (April 2026)

After the debugging saga in §13–14, the crew still produced intent text (`"I'll start by searching..."`). This section documents the **final root cause** and the definitive fix.

### 15.1 The Symptom
`output/solution.py` contained 1 line:
```
I'll start by searching for any existing technical plans or designs for this compound interest calculation task.
```

### 15.2 The Three Compounding Root Causes

| # | Cause | Effect |
|:---|:---|:---|
| 1 | `planning=True` | Meta-planner generated steps like "search for information" — agents had no search tools, so they output intention to do it |
| 2 | Task prompts referenced `"code execution tool"`, `"FileReadTool"`, `"FileWriterTool"` | Agents couldn't find these tools, so they described intending to use them as their final answer |
| 3 | Stale poisoned memory | Failed runs were saved to LanceDB at score=0.94, feeding bad context into every new run |

### 15.3 The Definitive Fix (3 Files + Memory Purge)

**`crew.py`:**
- Removed `planning=True` and `planning_llm`
- Changed LLM config from `LLM(model=..., is_litellm=True)` → `config['llm'] = config.pop('model')` (string passthrough, matches stock_picker_me)
- Added `allow_code_execution=True` + `code_execution_mode="unsafe"` to `senior_coder` and `code_reviewer`
- Removed `FileReadTool`, `DirectoryReadTool` imports (unused)
- Added `tracing=False`

**`tasks.yaml`:**
- Removed all references to tool names: "code execution tool", "FileReadTool", "FileWriterTool"
- Changed to: "Execute your code to verify it works" (generic — uses built-in execution)
- Changed `review_task` output to `output/review_report.txt` (not `output.txt`/`errors.txt`)

**`main.py`:**
- Stripped 250+ lines of debug instrumentation (NDJSON logging, compile checks, subprocess runs)
- Kept clean and simple like stock_picker_me: just `CoderMe().crew().kickoff(inputs=inputs)`

**Memory:**
- Deleted `./memory/` directory to purge all poisoned run artifacts

### 15.4 First Successful Run Results

**`output/solution.py`** — 341 lines of production Python generated by the `senior_coder` agent:
- Kahan summation algorithm for numerical stability
- Full type hints on every function
- Comprehensive docstrings (Args / Returns / Raises)
- Input validation (TypeError + ValueError for all edge cases)
- High-precision `Decimal` implementation option
- Convergence analysis function
- 11 concrete test cases

**`output/review_report.txt`** — Reviewer executed the code and confirmed:
```
✓ Test 0 terms: 0.0
✓ Test 1 term: 4.0
✓ Test 2 terms: 2.6666666667
✓ Test 3 terms: 3.4666666667
✓ Test 10 terms: 3.0418396189
✓ Test 100 terms: 3.1315929036
✓ Test 1000 terms: 3.1405926538
✓ Test 10000 terms: 3.1414926536   ← π ≈ 3.14149... (4 decimal places accurate)
✓ Test negative terms: Correctly raised ValueError
✓ Test invalid type: Correctly raised TypeError

π approximation (10,000 terms): 3.1414926536
True π value (math.pi):         3.1415926536
Absolute error:                  0.0001000000
Relative error:                  3.18e-05
```

**11/11 tests passed. Crew is fully operational.**

### 15.5 Updated Design Principles

9. **Never use `planning=True` with DeepSeek** — it generates meta-steps agents can't execute, causing intent-text output.
10. **Never reference tool names in prompts unless those tools are actually assigned to the agent** — if the tool isn't there, the agent outputs intent instead of results.
11. **Purge memory after a series of failed runs** — `rm -rf memory/` before the first clean run. Stale bad memories (score=0.94) poison every subsequent run.
12. **The string LLM passthrough is simpler and works.** `config['llm'] = config.pop('model')` (stock_picker_me pattern) works without `is_litellm=True`.

---

## 16. Multi-Model Agent Assignment (April 2026)

Different agents in the same crew can use different DeepSeek models. **Reasoner models think before they speak — critical for architecture design and bug detection.**

### Model Selection by Agent Role

| Agent | Model | Reasoning |
|:---|:---|:---|
| `code_planner` | `deepseek/deepseek-reasoner` (R1) | Plans the architecture — needs deep reasoning to define edge cases, data structures, and function signatures correctly |
| `senior_coder` | `deepseek/deepseek-chat` (V3) | Generates code from a clear blueprint — speed > depth |
| `code_reviewer` | `deepseek/deepseek-reasoner` (R1) | Bug-finding requires step-by-step logical reasoning — can't rush this |

### How to Set It in `agents.yaml`

```yaml
code_planner:
  model: deepseek/deepseek-reasoner

senior_coder:
  model: deepseek/deepseek-chat

code_reviewer:
  model: deepseek/deepseek-reasoner
```

The `model` → `llm` key rename in `crew.py` handles both:
```python
config = self.agents_config['code_planner'].copy()
if 'model' in config:
    config['llm'] = config.pop('model')  # works for both "deepseek-chat" and "deepseek-reasoner"
```

> [!NOTE]
> DeepSeek-R1 is **3–5× slower** than V3 and costs more per token. Only use it where reasoning depth genuinely matters (planner + reviewer). The coder just needs to translate a clear spec into code — V3 is sufficient.

### Updated Project Structure

```
coder_me/
├── src/coder_me/
│   ├── config/
│   │   └── agents.yaml    ← code_planner: deepseek-reasoner, senior_coder: deepseek-chat, code_reviewer: deepseek-reasoner
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── custom_tool.py
│   │   └── safe_code_executor.py   ← NEW (see §18)
│   ├── crew.py
│   └── main.py
```

---

## 17. The DeepSeek JSON Tool-Call Bug — Two Failure Modes

### Root Cause

When `allow_code_execution=True` is set (or a custom code tool is used), the agent communicates with the tool by serialising python code into a JSON string payload:

```json
{"code": "import numpy as np\n\ndef runge_kutta():\n    ...400 more lines..."}
```

DeepSeek V3 (and R1) frequently **fails to properly escape** newlines, quotes, and special characters in large Python scripts. This causes:

```
Error: Failed to parse tool arguments as JSON:
Unterminated string starting at: line 1 column 62 (char 61).
Please provide valid JSON arguments for the 'code_interpreter' tool.
```

CrewAI catches this, appends the error to the agent's context, and tells it to retry. The agent retries with the same broken format. **After `max_iter=10` retries, it hits the 600-second wall-clock timeout and crashes.**

### Why It's Worse With Bigger Scripts

| Script Size | Failure Rate |
|:---|:---:|
| < 100 lines (Pi calculator) | ~20% |
| 200–400 lines (N-Body / Schrödinger) | ~85% |
| 400+ lines (complex physics / QM) | ~99% |

### Failure Mode 1 — The Built-In `code_interpreter`

The default `allow_code_execution=True` attaches CrewAI's built-in `code_interpreter` tool. Large Python scripts JSON-serialised into this tool consistently fail. **Solution: replace with `SafeCodeExecutorTool` (§18).**

### Failure Mode 2 — Custom Tool Also Fails

Even after replacing with `SafeCodeExecutorTool`, the SAME error can still appear:
```
Tool safe_code_executor executed with result: Error: Failed to parse tool arguments as JSON:
Unterminated string starting at: line 1 column 10 (char 9)
```

**Root cause:** The `parse_tool_call_args` function in CrewAI is hit before Pydantic validation. Even custom tools are affected. **Solution: the regex monkey-patch (§18.2).**

---

## 18. The Production Fix — Belt-and-Suspenders (April 2026)

Both fixes are used together. `SafeCodeExecutorTool` eliminates the primary failure path. The regex monkey-patch is the fallback for when DeepSeek corrupts even the tool call wrapper.

```
DeepSeek generates code
    ↓
parse_tool_call_args() is called
    ↓ json.loads() succeeds?
  ┌─ YES ──► SafeCodeExecutorTool: code → tempfile → subprocess ✅
  └─ NO  ──► Regex patch extracts code string manually
                 ↓
             SafeCodeExecutorTool: code → tempfile → subprocess ✅
```

### Layer 1 — `SafeCodeExecutorTool`

Replaces the built-in `code_interpreter`. Code goes through the **filesystem, not JSON** — zero serialisation issues for any script size.

```python
# src/coder_me/tools/safe_code_executor.py
import os, subprocess, sys, tempfile
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class SafeCodeExecutorInput(BaseModel):
    code: str = Field(..., description="Complete raw Python source code to execute.")
    timeout: int = Field(default=60, description="Max seconds before killing the process.")

class SafeCodeExecutorTool(BaseTool):
    name: str = "safe_code_executor"
    description: str = (
        "Execute Python source code by writing it to a temp file and running it "
        "via subprocess. Pass COMPLETE raw Python code (no markdown fences). "
        "Returns combined stdout and stderr."
    )
    args_schema = SafeCodeExecutorInput

    def _run(self, code: str, timeout: int = 60) -> str:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
                f.write(code)
                tmp_path = f.name
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True, text=True, timeout=timeout
            )
            header = "✅ EXECUTION PASSED" if result.returncode == 0 else f"❌ EXECUTION FAILED (exit {result.returncode})"
            parts = [header]
            if result.stdout.strip(): parts.append(f"\n--- STDOUT ---\n{result.stdout.strip()}")
            if result.stderr.strip(): parts.append(f"\n--- STDERR ---\n{result.stderr.strip()}")
            return "\n".join(parts)
        except subprocess.TimeoutExpired:
            return f"❌ EXECUTION TIMED OUT after {timeout}s."
        except Exception as exc:
            return f"❌ EXECUTION ERROR: {exc}"
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
```

**Wiring in `crew.py`:** Replace `allow_code_execution=True` with:
```python
from coder_me.tools.safe_code_executor import SafeCodeExecutorTool

return Agent(
    config=config,
    tools=[SafeCodeExecutorTool()],  # filesystem-based, no JSON issues
    max_iter=10,
    max_retry_limit=3,
    max_execution_time=600,
    allow_delegation=False,
    verbose=True,
)
```

> [!IMPORTANT]
> Do **NOT** also set `allow_code_execution=True` — it adds the built-in `code_interpreter` back, giving DeepSeek a second broken path to choose from.

### Layer 2 — Regex Monkey-Patch (Safety Net)

Even with `SafeCodeExecutorTool`, DeepSeek can fail to JSON-encode the tool call wrapper itself. This fallback catches those cases and manually extracts the code string using regex. Both tool names must be covered.

```python
# crew.py — immediately after the Docker patch
import json as _json
import re as _re
import crewai.utilities.agent_utils as _agent_utils
_original_parse = _agent_utils.parse_tool_call_args

def _patched_parse_tool_call_args(func_args, func_name, call_id, original_tool=None):
    if isinstance(func_args, str) and func_name in ["code_interpreter", "safe_code_executor"]:
        try:
            return _json.loads(func_args), None
        except _json.JSONDecodeError:
            match = _re.search(
                r'(?:"code"|\'code\')\s*:\s*["\'](.*)["\']\s*}?\s*$', func_args, _re.DOTALL
            )
            if match:
                code_content = match.group(1)
                code_content = code_content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                return {"code": code_content}, None
    return _original_parse(func_args, func_name, call_id, original_tool)

_agent_utils.parse_tool_call_args = _patched_parse_tool_call_args
```

> [!NOTE]
> The monkey-patch covers **both** `"code_interpreter"` (built-in) and `"safe_code_executor"` (custom). Covering only one leaves the other unprotected.

### Final Comparison Table

| Approach | Primary Path | Fallback | Script Size Limit | Reliable? |
|:---|:---:|:---:|:---:|:---:|
| `allow_code_execution=True` (vanilla) | `code_interpreter` JSON | ❌ None | ~100 lines | ❌ |
| Regex patch only | `code_interpreter` JSON | Regex | ~200 lines | ⚠️ |
| `SafeCodeExecutorTool` only | Filesystem | ❌ None | Unlimited | ✅ mostly |
| **`SafeCodeExecutorTool` + Regex patch** | **Filesystem** | **Regex** | **Unlimited** | **✅ Production** |

### Updated Design Principles

13. **Never use `allow_code_execution=True` alone with DeepSeek on large scripts.** Replace with `SafeCodeExecutorTool`.
14. **`SafeCodeExecutorTool` is the correct primary path.** Code goes filesystem → subprocess, no JSON escaping needed.
15. **The regex monkey-patch is the safety net, not the solution.** Keep BOTH. The patch covers the edge case where DeepSeek corrupts even the tool call wrapper JSON.
16. **Cover both tool names in the monkey-patch.** `func_name in ["code_interpreter", "safe_code_executor"]` — if you only cover one, DeepSeek can still hit the bug via the other name.


