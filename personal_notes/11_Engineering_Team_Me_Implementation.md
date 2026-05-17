# Chapter 11: EngineeringTeamMe — The Full-Stack Autonomous Software Crew

The **EngineeringTeamMe** project is the evolution of the CoderMe pipeline. While CoderMe focused on writing and validating a single python script, EngineeringTeamMe acts as a complete, autonomous software development team. It takes high-level business requirements and autonomously produces a technical design document, a production-ready backend module, a Gradio frontend UI, and a comprehensive suite of unit tests.

---

## 1. The Core Evolution: From Coder to Full Engineering Team

The move from a 3-agent to a 4-agent crew fundamentally shifts the project from "script generation" to "software engineering". 

Key architectural shifts from the previous pipeline:
- **Separation of Concerns:** Design, Backend coding, Frontend UI, and Testing are fully isolated tasks performed by specialized agents.
- **Model Routing:** Heavy use of `deepseek-reasoner` (R1) for complex architectural and implementation tasks, while using `deepseek-chat` (V3) for straightforward tasks like writing tests.
- **Robust Output Handling:** Native markdown fence stripping directly in the main execution flow to guarantee runnable Python files.
- **Targeted Tooling:** The `SafeCodeExecutorTool` is restricted *only* to the backend engineer to verify the core module, preventing frontend/test engineers from getting distracted by execution timeout loops.

---

## 2. The 4-Agent Sequential Pipeline

The crew strictly enforces a sequential **Design → Backend → Frontend → Test** process.

| Agent | Role | Model | Key Features |
| :--- | :--- | :--- | :--- |
| **engineering_lead** | Architect | `deepseek/deepseek-reasoner` | Produces the `.md` technical design blueprint |
| **backend_engineer** | Python Coder | `deepseek/deepseek-reasoner` | Writes the core backend module. Uses `SafeCodeExecutorTool` to verify |
| **frontend_engineer** | UI Developer | `deepseek/deepseek-reasoner` | Builds `app.py` Gradio interface demonstrating the backend |
| **test_engineer** | QA Engineer | `deepseek/deepseek-chat` | Writes comprehensive `unittest` suite |

> [!TIP]
> **Why `deepseek-reasoner` vs `deepseek-chat`?**
> R1 (reasoner) thinks before it speaks, making it crucial for complex tasks like architectural design, bug-free implementation, and UI logic mapping. However, for a QA engineer who is simply writing `unittest` functions based on a finalized design and codebase, V3 (chat) is significantly faster, cheaper, and entirely sufficient.

---

## 3. Implementation Step 1: Agent Configuration (`agents.yaml`)

Agents are configured with explicit dependencies on the input variables `{requirements}`, `{module_name}`, and `{class_name}`. 

```yaml
engineering_lead:
  goal: >
    Take the high level requirements described here and prepare a detailed design for the backend developer;
    everything should be in 1 python module...
  llm: deepseek/deepseek-reasoner

backend_engineer:
  goal: >
    Write a python module that implements the design described by the engineering lead...
    The module should be named {module_name} and the class should be named {class_name}
  llm: deepseek/deepseek-reasoner
```

> [!IMPORTANT]
> The YAML strictly specifies the LLM provider mapping. The `crew.py` model string passthrough parses `llm: deepseek/deepseek-reasoner` seamlessly into the LiteLLM backend.

---

## 4. Implementation Step 2: Task Architecture (`tasks.yaml`)

The tasks define the exact output formatting expectations. LLMs notoriously inject markdown (````python`) around code blocks. The task definitions attempt to prevent this, but we also enforce it via post-processing (see Section 8).

```yaml
coding_task:
  description: >
    ...
    IMPORTANT: Output ONLY the raw Python code without any markdown formatting, code block delimiters, or backticks.
    The output should be valid Python code that can be directly saved to a file and executed.
  agent: backend_engineer
  context:
    - design_task
  output_file: output/{module_name}
```

> [!TIP]
> **Explicit Context Chaining:** Notice `context: [design_task]`. We do not rely on CrewAI's auto-context passing. Explicit chaining ensures the backend engineer starts iteration 1 with the full design document loaded in context.

---

## 5. Advanced Agent Fixes (`crew.py`)

The Engineering crew relies on several battle-tested monkey-patches to stabilize DeepSeek interactions with CrewAI.

### 5.1 Docker Validation Bypass
`allow_code_execution=True` defaults to Docker execution. Even when using our custom `SafeCodeExecutorTool`, CrewAI's initialization sequence can trip over missing Docker installations.

```python
def _noop_docker_check(self) -> None:
    pass
import crewai.agent.core as _crewai_core
_crewai_core.Agent._validate_docker_installation = _noop_docker_check
```

### 5.2 The Regex Monkey-Patch (JSON Parsing)
DeepSeek models often fail to properly escape quotes and newlines when using tools with large code blocks. The crew implements a regex fallback for `parse_tool_call_args` to manually extract code payloads when standard `json.loads` fails.

```python
def _patched_parse_tool_call_args(func_args, func_name, call_id, original_tool=None):
    if isinstance(func_args, str) and func_name in ["code_interpreter", "safe_code_executor"]:
        try:
            return json.loads(func_args), None
        except json.JSONDecodeError:
            # Fallback for DeepSeek's raw multi-line strings breaking JSON
            match = re.search(r'(?:"code"|\'code\')\s*:\s*["\'](.*)["\']\s*}?\s*$', func_args, re.DOTALL)
            if match:
                code_content = match.group(1).replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                return {"code": code_content}, None
```

### 5.3 Plain JSON Wrapper for Memory
DeepSeek rejects OpenAI-style structured `response_format` schemas. To enable persistent LanceDB memory, we wrap the memory LLM to report `supports_function_calling() -> False`, forcing CrewAI's fallback plain-text analyzer branch.

```python
class _PlainJsonLLM:
    def supports_function_calling(self) -> bool:
        return False
```

---

## 6. The Execution Engine: `SafeCodeExecutorTool`

To bypass tool-call hanging issues, we restrict code execution ONLY to the `backend_engineer` and utilize the `SafeCodeExecutorTool`.

```python
@agent
def backend_engineer(self) -> Agent:
    return Agent(
        config=config,
        tools=[SafeCodeExecutorTool()],  # temp-file execution — no JSON escaping issues
        max_iter=10,
        max_retry_limit=3,
        max_execution_time=600,
        ...
    )
```

The tool takes raw Python, writes it to a `NamedTemporaryFile` on the host machine, executes it via `subprocess.run()`, and returns standard out/error to the agent. This entirely eliminates the context-length limitations and string-escaping nightmares of the default `code_interpreter`.

---

## 7. The Entry Point: Markdown Stripping (`main.py`)

No matter how many times you prompt an LLM to "Output ONLY the raw Python code without any markdown formatting", it will eventually wrap code in ````python ... ````. 

The `main.py` entry point actively post-processes all generated `.py` files to guarantee they are executable.

```python
print("\n[Post-Processing] Stripping LLM markdown code blocks from outputs...")
for py_file in glob.glob("output/*.py"):
    with open(py_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Strip exact leading ```python (or similar) and trailing ```
    cleaned = re.sub(r'^```[a-zA-Z]*\n', '', content.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r'\n```$', '', cleaned)
    
    if cleaned != content:
        with open(py_file, "w", encoding="utf-8") as f:
            f.write(cleaned)
```

---

## 8. Standalone Agent Execution: `run_test_only.py`

Sometimes a 10-minute generation completes flawlessly, but the unit tests are slightly misaligned. Re-running the entire 4-agent crew burns unnecessary tokens and time. 

The project includes `run_test_only.py`, a specialized script that creates a mini-crew restricted solely to the `test_engineer`. It reads the *already generated* `accounts.py` and `accounts_design.md` from the disk and injects them as inline context.

```python
# 2. Create a standalone task that passes the existing code directly
standalone_test_task = Task(
    description=(
        "Write comprehensive unit tests for the following Python module..."
        f"=== EXISTING MODULE CODE ===\n{accounts_code}\n\n"
        f"=== TECHNICAL DESIGN ===\n{design_doc}\n\n"
    ),
    agent=test_agent,
    output_file="output/test_accounts.py",
)

# 3. Create a mini-crew with JUST the test engineer
mini_crew = Crew(agents=[test_agent], tasks=[standalone_test_task])
mini_crew.kickoff()
```

> [!IMPORTANT]
> **Token & Time Optimization:** This pattern is a lifesaver in production autonomous coding. Always decouple your pipeline elements so that failing sub-components (like tests or UI) can be re-prompted without re-generating the core architecture.

---

## 9. Battle Log: Errors Encountered & Fixes Applied

This section documents every real error we hit during development and execution, in chronological order. These are not theoretical — each one caused a crashed run, wasted tokens, or required manual intervention.

### 9.1 Error: `code_interpreter` JSON Parsing Loop (Run #1)
**Symptom:**
```
Tool code_interpreter executed with result: Error: Failed to parse tool arguments as JSON:
Unterminated string starting at: line 1 column 54 (char 53)
```
The `backend_engineer` and `test_engineer` agents both had `allow_code_execution=True`, which attaches CrewAI's built-in `code_interpreter` tool. DeepSeek would attempt to send 200+ lines of Python as a JSON string value, but consistently failed to escape `\n`, `"`, and `'` characters correctly. The agent would retry the same malformed call 3-5 times, burning tokens in a loop until hitting `max_iter` or `max_execution_time`.

**Fix:** Built `SafeCodeExecutorTool` (`tools/safe_code_executor.py`). This custom CrewAI tool accepts the code string via Pydantic (which handles parsing), writes it to a `NamedTemporaryFile` on disk, and executes via `subprocess.run()`. Code never travels through JSON serialization. Replaced `allow_code_execution=True` with `tools=[SafeCodeExecutorTool()]` on the `backend_engineer`.

**Result:** The `backend_engineer` immediately executed its code on the first attempt and received `✅ EXECUTION PASSED` with full stdout.

---

### 9.2 Error: `safe_code_executor` Still Failing JSON Parse (Run #2)
**Symptom:**
```
Tool safe_code_executor executed with result: Error: Failed to parse tool arguments as JSON:
Unterminated string starting at: line 1 column 10 (char 9)
```
Even with the custom tool, the `test_engineer` hit the exact same JSON loop.

**Root Cause:** The regex monkey-patch in `crew.py` was only watching for `func_name == "code_interpreter"`. When we renamed the tool to `safe_code_executor`, the patch ignored it entirely, falling back to the default broken `json.loads()`.

**Fix:** Updated the condition to `func_name in ["code_interpreter", "safe_code_executor"]`. Also removed `SafeCodeExecutorTool` from the `test_engineer` entirely — it only needs to *write* test code to `output_file`, not execute it.

---

### 9.3 Error: ` ```python ` Markdown Fences in Output Files (Run #1-3)
**Symptom:**
```
SyntaxError: invalid syntax (line 1)
```
When running `uv run python output/test_accounts.py`, the file started with ` ```python ` — a markdown code fence that is not valid Python.

**Root Cause:** Despite explicit prompt instructions ("Output ONLY the raw Python code without any markdown formatting"), DeepSeek's training data is so heavily markdown-oriented that it wraps code outputs in fences approximately 60-70% of the time.

**Fix:** Added an automated post-processing step in `main.py` that runs immediately after `.kickoff()` completes. It regex-strips leading ` ```python ` and trailing ` ``` ` from every `.py` file in the `output/` directory. The same logic was added to `run_test_only.py`.

---

### 9.4 Error: Truncated Test File — Missing `unittest.main()` (Run #2)
**Symptom:** Running `uv run python output/test_accounts.py` produced **zero output** — no test results, no errors, nothing.

**Root Cause:** The test engineer generated 400+ lines of test code, hitting DeepSeek's max output token limit. The file was truncated mid-function, missing:
```python
if __name__ == '__main__':
    unittest.main(verbosity=2)
```
Without this entry point, Python imports the file but never executes the tests.

**Fix:** Manually appended the missing `unittest.main(verbosity=2)` block. For future runs, the `run_test_only.py` script explicitly instructs the agent to include this block in its prompt.

---

### 9.5 Error: `KeyError: 'AAPL'` — Case Insensitive Symbol Bug (Run #3)
**Symptom:**
```
ERROR: test_buy_shares_case_insensitive_symbol
KeyError: 'AAPL'
```
33 of 34 tests passed. The failing test called `account.buy_shares("aapl", 10.0)` (lowercase) and then asserted `self.account.holdings["AAPL"]` (uppercase).

**Root Cause:** The `backend_engineer` correctly implemented case-insensitive lookup in `get_share_price()` by calling `symbol.upper()`, but forgot to normalize the symbol before storing it in `self.holdings` inside `buy_shares()` and `sell_shares()`. So `holdings` contained `{"aapl": 10.0}` instead of `{"AAPL": 10.0}`.

**Fix:** Added `symbol = symbol.upper()` at the top of both `buy_shares()` and `sell_shares()` in `accounts.py`.

**Result:** 34/34 tests passed.

> [!TIP]
> **This is exactly the value of autonomous multi-agent pipelines.** The Test Engineer organically discovered a real logic bug that the Backend Engineer introduced. In a traditional workflow, this would require a human code reviewer. Here, the agents caught it themselves.

---

### 9.6 Error: `ModuleNotFoundError: No module named 'gradio'` (Manual Run)
**Symptom:** Running `uv run app.py` in the output directory failed because `gradio` wasn't in the project dependencies.

**Fix:** `uv add gradio` — added it to the project's `pyproject.toml`.

---

## 10. Output Architecture

The final payload output to `./output/` represents a completely deployable repository structure:

| File | Produced By | Purpose |
| :--- | :--- | :--- |
| `accounts.py_design.md` | `engineering_lead` | Architectural contract and specifications. |
| `accounts.py` | `backend_engineer` | Production code implementing the design. |
| `app.py` | `frontend_engineer` | Run-ready Gradio UI web application. |
| `test_accounts.py` | `test_engineer` | Comprehensive test suite targeting the backend. |

When testing against a complex Trading Account specification (Deposits, Withdrawals, Share purchasing, Portfolio Valuations), the crew successfully generates a 400+ line backend module with zero syntax errors, and a 34-test completely passing unit test suite, alongside a functional Gradio interface.

---

---

## Chapter 11B: Structured Output Refactor — 7-Agent Dynamic Pipeline

This section documents the major refactor that transformed the original 4-agent static YAML crew into a dynamic 7-agent pipeline with structured Pydantic output, multi-model routing, and imperative crew construction.

### The Refactored Architecture (7 Agents)

| Agent | Role | Model | Created When |
| :--- | :--- | :--- | :--- |
| **lead** | Software Architect | `deepseek-reasoner` | Always |
| **backend** | Python Engineer | `deepseek-chat` | Always |
| **frontend** | Gradio UI Engineer | `deepseek-chat` | `needs_frontend=True` |
| **tester** | QA Engineer | `deepseek-chat` | `needs_tests=True` |
| **reviewer** | Code Reviewer | `deepseek-reasoner` | Always |
| **writer** | Technical Writer | `deepseek-chat` | `needs_docs=True` |

**Model strategy:** `reasoner` for architecture and code review (needs deep reasoning), `chat` for implementation agents (speed + lower cost).

### Key Changes

#### 1. Structured Pydantic Output (`models.py` — NEW FILE)
Every agent now produces a typed, validated Pydantic model instead of free-form text:

| Model | Produced By | Fields |
| :--- | :--- | :--- |
| `RequirementsAnalysis` | Phase 0 (direct API call) | module_name, class_name, core_features, complexity, needs_frontend/tests/docs, reason |
| `DesignDoc` | lead | module_name, class_name, methods[MethodSpec], dependencies, design_notes |
| `CodeModule` | backend | source_code, verified |
| `FrontendModule` | frontend | source_code |
| `TestSuite` | tester | source_code, all_passing |
| `ReviewReport` | reviewer | approved, issues, suggestions, score |
| `ProjectDocs` | writer | readme, examples |
| `PipelineOutput` | Aggregator | design, code, frontend?, tests?, review?, docs? |

This ensures:
- **Type safety** — downstream agents receive guaranteed schema-compliant data
- **Deterministic output** — no markdown fence stripping needed for code
- **Runtime validation** — Pydantic validates at parse time, fails fast on malformed output
- **Clean data flow** — `task_output.pydantic` gives typed objects, not raw strings

#### 2. Imperative Crew Builder (`crew.py` — REWRITTEN)
Replaced the static `@CrewBase` decorator + YAML config with a fully programmatic builder:

```python
# Phase 0: Fast analysis (single LLM call, no Crew overhead)
analysis = await _analyze_requirements(req, module, class_name)

# Phase 1: Build dynamic crew based on analysis
crew, output = build_pipeline(analysis)

# Phase 2-3: Run + extract
result = crew.kickoff()
# result.tasks_output[i].pydantic → typed model
```

Key design decisions:
- `_analyze_requirements()` uses a direct DeepSeek API call with `response_format="json_object"` — avoids spinning up a full Crew just to decide what to build
- `build_pipeline()` dynamically constructs agent/task lists — only creates frontend/tester/writer agents when needed
- Agent factory maps `"chat"` → `deepseek-chat`, `"reasoner"` → `deepseek-reasoner` for concise config
- SafeCodeExecutorTool stays restricted to the backend agent only

#### 3. 3-Phase Execution Flow (`main.py` — REWRITTEN)

```
Phase 0: Requirements Analysis
  └─ Direct DeepSeek API call → RequirementsAnalysis (JSON)

Phase 1: Build Crew
  └─ build_pipeline(analysis) → Crew with dynamic agents/tasks

Phase 2: Run Pipeline
  └─ crew.kickoff() → CrewOutput with tasks_output[] of typed models

Phase 3: Extract + Write Files
  └─ Iterate tasks_output, check pydantic type, write to output/
```

#### 4. Removed Redundancy
- **`agents.yaml` / `tasks.yaml`** — No longer used. Config was duplicated between YAML and Python. Now all config lives in `crew.py`'s imperative builder.
- **Markdown fence post-processing** — No longer needed. Structured output forces the LLM to return valid JSON matching the Pydantic schema. Code is extracted from typed fields, not free-text that needs regex cleaning.
- **`run_test_only.py`** — No longer needed. The pipeline produces typed models; individual components can be re-generated by re-running specific tasks.

### File Manifest (Current)

| File | Status | Purpose |
| :--- | :--- | :--- |
| `models.py` | **NEW** | All Pydantic structured output models |
| `crew.py` | **REWRITTEN** | Imperative crew builder with dynamic tasks |
| `main.py` | **REWRITTEN** | 3-phase async pipeline runner |
| `tools/safe_code_executor.py` | Unchanged | Temp-file code execution |
| `config/agents.yaml` | Orphaned | Replaced by imperative builder |
| `config/tasks.yaml` | Orphaned | Replaced by dynamic tasks |
| `run_test_only.py` | Orphaned | Superseded by structured output extraction |

### Testing Notes

To run the refactored pipeline:
```bash
cd /path/to/engineering_team_me
uv run python -m engineering_team_me.main
```

Required environment:
- `DEEPSEEK_API_KEY` set in `.env` (at project root) or environment
- `output/` directory created automatically

---

## Structured Output vs Free-Text (Design Decision)

This project originally used **free-text output** — tasks dump raw markdown/code to `output_file` without schema enforcement. As of the Chapter 11B refactor, it now uses **structured Pydantic output**.

### Current Approach (Free-Text)
```yaml
coding_task:
  expected_output: "A complete Python module..."
  output_file: output/accounts.py
```
- LLM writes free-form text → post-processing needed (markdown fence stripping in `main.py`)
- Best for generating code, prose, design documents

### Structured Output Alternative
```python
from pydantic import BaseModel

class CodeModule(BaseModel):
    module_name: str
    class_name: str
    source_code: str
    dependencies: list[str]

Task(config=..., output_pydantic=CodeModule)
```
- LLM forced to return valid JSON matching schema → validated at runtime
- Access data as typed objects: `task_output.module_name`
- Best for API responses, JSON configs, data extraction

### Why Free-Text for This Project
This crew generates **code files** — unstructured text that LLMs handle naturally. Structured output would constrain the format unnecessarily. The `_PlainJsonLLM` wrapper in `crew.py` handles the reverse case: it forces plain-text mode for DeepSeek (which rejects CrewAI's structured response schemas).
