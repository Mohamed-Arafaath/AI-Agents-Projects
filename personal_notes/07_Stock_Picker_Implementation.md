# Chapter 7: StockPickerMe — Deep Market Intelligence & Technical Auditing

The **StockPickerMe** project is a high-stakes financial research unit designed for an AI Agency. It moves beyond simple "web search" bots by implementing **Technical DNA Auditing**, where a company's internal tech stack is treated as a core valuation metric.

---

## 1. The Core Insight: Why News-Bots Fail
The primary failure of most financial AI is **Hype-Recirculation**. Typical bots just summarize what they find on Yahoo Finance. 

### The Solution: The "Technical Auditor" Pattern
StockPickerMe assumes that profit in the AI era comes from **Efficiency**. Instead of just looking at earnings, the crew is instructed to:
1.  **Identify the Tech DNA:** Does the company use n8n, Claude Code, or self-hosted LLMs?
2.  **Cross-Reference Margins:** Does their technical delivery model actually translate to higher EBITDA margins?
3.  **Validate Hype:** Is the company actually building "Agentic Solutions" or just slapping "AI" on their website?

---

## 2. The 5-Agent Architecture

The Unit follows a strict manager-specialist hierarchy, mirroring the `followup_agent` pattern:

| Agent | Responsibility | Key Feature |
| :--- | :--- | :--- |
| **Query Refiner** | Context Architect | Acts as the "Stakeholder Interviewer." |
| **Market Scout** | Trend Identifier | Uses `SerperDevTool` for deep tool-stack validation. |
| **Financial Researcher** | Technical Auditor | Rigorous auditing of revenue vs. unit economics. |
| **Investment Strategist** | Senior Decision Engine | Assigns risk-adjusted weights to choices. |
| **Project Manager** | Strategic Coordinator | Ensures "Executive Narrative" meets C-suite standards. |

---

## 3. Implementation Step 1: The "Human-in-the-Loop" Gate
To prevent "Runaway Token Spend," the crew must pause after the first task.

### The Refinement Code (`crew.py`)
```python
@task
def refinement_task(self) -> Task:
    return Task(
        config=self.tasks_config['refinement_task'],
        human_input=True # <--- MANDATORY pause for user validation
    )
```

### The "Truly Once" Input Architecture (`tasks.yaml`)
To eliminate the "Double-Approval" friction common in CrewAI, we have split the refinement process into two distinct tasks:
1. **`refinement_task` (The Interview):** This task is the **only** one with `human_input: true`. It generates the 3-5 questions and waits for your input. Once you provide answers and hit Enter, this task is marked as 100% complete and the crew moves forward.
2. **`scout_task` (The Research):** This task starts by **silently** reviewing the feedback from the previous task, finalizing the research brief internally, and immediately beginning the Market Scouting. 

> [!TIP]
> **Agency Pro-Tip:** This architectural split is the standard for high-performance AI Agencies. By separating the *Interactive Phase* from the *Execution Phase*, you minimize the number of times a human "orchestrator" has to interact with the terminal.

---

## 4. Implementation Step 2: Forced JSON Strategy
To ensure the output is "Machine Readable" for dashboards, we use **Pydantic Model Enforcement**. The `Market Scout` is forbidden from returning conversational text.

### The Model Specification
```python
class TrendingCompanyResearch(BaseModel):
    name: str = Field(description="Company name")
    market_position: str = Field(description="Competitive analysis")
    future_outlook: str = Field(description="Growth prospects")
    investment_potential: str = Field(description="Suitability for capital")

class TrendingCompanyResearchList(BaseModel):
    research_list: List[TrendingCompanyResearch]
```

---

## 5. Technical Standard: The Multi-Piped Output
In professional agency work, we don't just give a final PDF. We create a **"Paper Trail"** of reasoning. Each task in `tasks.yaml` has a specific downstream file:

- **Stage 1 (Raw Intelligence):** `output/market_intelligence.json`
- **Stage 2 (The Numbers):** `output/financial_audit.md`
- **Stage 3 (The Pick):** `output/investment_recommendation.md`
- **Stage 4 (The Report):** `output/executive_summary.md`

> [!TIP]
> **Agency Pro-Tip: The "Quality Control" Task**
> Always add a final task assigned to a `project_manager`. This agent's only job is to cross-reference the data from previous steps and fix formatting errors. This ensures the recommendation doesn't hallucinate numbers that the Researcher didn't provide.

---

## 6. Execution: The "Training" Loop
CrewAI allows you to **train** your agents on correct/incorrect results.
```bash
# From the project root
uv run stock_picker_me train 10 my_training_log.pkl
```
- **Training Concept:** You provide the "Industry" (e.g. AI LLMs), run the crew, and then rate the output. The crew stores the learning in a `.pkl` file to improve its reasoning "instincts" in future runs.

---

## 7. Real-Time Alerting (Push Notification Pattern)
In professional Agency environments, research tasks can take several minutes. To improve the User Experience, we implement **Deterministic Notifications** to alert the stakeholder as soon as a milestone is reached.

### The Push Notification Tool
Located in `tools/push_tool.py`, this tool uses the **Pushover API** to send instant messages to the user's mobile device or desktop.

### Double-Layered Integration
To ensure maximum reliability, we implement notifications at three levels:
1. **Agent-Led (Autonomous):** The `market_scout` is given the `PushNotificationTool` in its toolset. This allows it to send custom alerts if it finds something "groundbreaking" during the search.
2. **Intermediate (Milestone):** We use a `callback` on the `scout_task` to alert the user when the raw research is ready.
3. **Terminal (Final):** A final `callback` on the `quality_control_task` notifies the user that the entire project is polished and the Executive Summary is ready for review.

```python
# Terminal Notification Example
@task
def quality_control_task(self) -> Task:
    return Task(
        config=self.tasks_config['quality_control_task'],
        output_file='output/executive_summary.md',
        callback=lambda output: PushNotificationTool()._run(
            message=f"🏁 Project Complete! Report ready."
        )
    )
```

---

---

## 8. Process Comparison: Sequential vs. Hierarchical (Manager Mode)

Understanding the difference between these two execution patterns is crucial for building elite multi-agent systems.

| Feature | **Sequential Process** | **Hierarchical Process** |
| :--- | :--- | :--- |
| **Workflow** | Linear and Predictable. | Dynamic and Delegated. |
| **Structure** | Agents follow a fixed list of tasks in order. | A **Manager Agent** sits above the team, assigning tasks. |
| **Manager Role** | None (You are the architect). | Active (The Manager decides "Who" does "What" and "When"). |
| **Execution** | Task A must finish before Task B starts. | Manager can iterate, skip, or re-assign tasks based on quality. |
| **Best For** | Standardized, step-by-step processes. | Complex research requiring high-level coordination. |
| **Efficiency** | Very efficient (minimum LLM calls). | Resource intensive (extra logic for the Manager). |

### Why use Hierarchical for StockPickerMe?
In an elite stock-picking agency, the **Manager** acts like a Chief Investment Officer (CIO). 
- **Validation:** If the `market_scout` finds low-quality companies, the Manager can force them to research better ones before the `financial_analyst` wastes time on them.
- **Dynamic Handoffs:** The Manager ensures the context is passed perfectly between research tiers using high-level reasoning.

### Technical Implementation
1. **Manager Agent:** You must specify a `manager_llm` or a `manager_agent`.
2. **Process Toggle:** Set `process=Process.hierarchical` in the `Crew` definition.

---

## 9. Memory Architecture: The Full Debugging Saga (CrewAI v1.12–1.14)

This section documents every error encountered while enabling persistent memory for StockPickerMe, why each one happened, and the final working solution.

### 9.1 The Goal
Enable **persistent cross-session memory** so the crew remembers previous research runs — user constraints, past company analyses, and investment preferences. The reference course project (`stock_picker`) used the **legacy memory API**:

```python
# OLD API (CrewAI < 1.0 — reference project)
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory, UserMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

Crew(
    memory=True,
    long_term_memory=LongTermMemory(storage=LTMSQLiteStorage(db_path="./memory/ltm.db")),
    short_term_memory=ShortTermMemory(storage=RAGStorage(embedder_config={...})),
    entity_memory=EntityMemory(storage=RAGStorage(embedder_config={...})),
)
```

**What each legacy class was responsible for:**

| Class | What it stored | Storage backend |
| :--- | :--- | :--- |
| `ShortTermMemory` | Recent context **within** the current run (inter-task handoffs) | `RAGStorage` (vector DB) |
| `LongTermMemory` | Cross-session persistent facts — past research, preferences | `LTMSQLiteStorage` (SQLite file) |
| `EntityMemory` | Named entities — companies, people, tools mentioned in research | `RAGStorage` (vector DB) |
| `UserMemory` | User-specific constraints — risk tolerance, capital, past decisions | `RAGStorage` (vector DB) |

> [!IMPORTANT]
> **This legacy API does NOT exist in CrewAI v1.x (1.12+).** The `long_term_memory`, `short_term_memory`, and `entity_memory` parameters were removed. They were replaced by the unified `Memory` class. Importing them will throw `ImportError`.

**Industry-Standard Alternatives (outside CrewAI):**

| Solution | Best For | Hosted? | Cost |
| :--- | :--- | :--- | :--- |
| **LanceDB** (CrewAI default) | Local vector search, zero infra | ❌ Local | Free |
| **SQLite** (via `LTMSQLiteStorage`) | Simple persistent KV storage | ❌ Local | Free |
| **Mem0** | Drop-in memory layer for any LLM app | ✅ Cloud | Free tier |
| **Pinecone** | Production-scale cloud vector DB | ✅ Cloud | Paid |
| **Weaviate** | Self-hosted, full hybrid search | Both | Free OSS |
| **Redis** | Ultra-fast session/short-term memory | Both | Free OSS |
| **PostgreSQL + pgvector** | Already have SQL DB, want vector search | ❌ Self | Free OSS |

> [!TIP]
> For local, free-tier agentic projects: **LanceDB (via CrewAI `Memory`) + `_hash_embedder`** is the perfect combo — no API calls, no infra, no cost, persistent across sessions.


### 9.2 CrewAI v1.x Unified Memory

In v1.x, memory is a single `Memory` object that handles everything:

```python
from crewai.memory import Memory

memory = Memory(
    llm="gpt-4o-mini",       # LLM for memory analysis (scope, categories, importance)
    embedder=my_embedder,     # Embedding function for vector search
    storage="./memory",       # Local LanceDB storage path
)

Crew(memory=memory)  # Pass the object directly
```

The `Memory` class **requires an LLM** because it does "smart" analysis:
- **On save:** LLM infers scope, categories, importance, and extracts entities
- **On recall:** LLM distills the query into sub-queries and selects scopes
- **On consolidation:** LLM decides whether to merge, update, or insert new records

### 9.3 Error #1: DeepSeek 400 — `response_format` Rejection

**What happened:**
```
OpenAI API call failed: Error code: 400 - {'error': {'message': 'This response_format type is unavailable now'}}
```

**Root Cause:**
CrewAI's `memory/analyze.py` checks `llm.supports_function_calling()`. When it returns `True`, the code calls:
```python
response = llm.call(messages, response_model=MemoryAnalysis)  # structured JSON schema
```
This adds a `response_format` parameter to the API call. **DeepSeek's API claims to support function calling but rejects structured JSON output schemas** — a known DeepSeek limitation.

**The failing code path in `analyze.py`:**
```python
def analyze_for_save(content, existing_scopes, existing_categories, llm):
    if getattr(llm, "supports_function_calling", lambda: False)():
        response = llm.call(messages, response_model=MemoryAnalysis)  # ← FAILS for DeepSeek
    else:
        response = llm.call(messages)  # ← Plain text branch (parses JSON from string)
```

**The Fix — `_PlainJsonLLM` Wrapper:**
```python
class _PlainJsonLLM:
    """Forces DeepSeek into plain-text JSON mode."""
    def __init__(self, model: str):
        from crewai.llm import LLM
        self._inner = LLM(model=model)

    def supports_function_calling(self) -> bool:
        return False  # ← Forces the plain-text branch

    def call(self, messages, **kwargs):
        kwargs.pop("response_model", None)  # strip if somehow passed
        return self._inner.call(messages, **kwargs)

    def __getattr__(self, name):
        return getattr(self._inner, name)
```

This forces `analyze.py` to take the `else` branch (plain text), where DeepSeek returns JSON as a string and CrewAI parses it with `json.loads()`.

---

### 9.4 Error #2: Gemini 429 — Free Tier Quota Exhausted

**What happened (when we switched to Gemini for memory LLM):**
```
Google Gemini API error: 429 - RESOURCE_EXHAUSTED
Quota exceeded for metric: generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash
```

**Root Cause:**
The Gemini free tier has strict daily limits. Memory analysis fires multiple LLM calls per task (extraction, save analysis, consolidation, query analysis). With a 5-task crew, this easily burns through the daily free quota.

**Why it's non-blocking:** CrewAI's `analyze.py` wraps all LLM calls in `try/except` and falls back to safe defaults:
```python
except Exception as e:
    _logger.warning("Memory save analysis failed, using defaults: %s", e)
    return _SAVE_DEFAULTS  # ← Still saves the memory, just without smart categorization
```

**Alternatives:**

| Solution | Cost | Quality |
| :--- | :--- | :--- |
| `_PlainJsonLLM("deepseek/deepseek-chat")` | $0.001/run | ⭐⭐⭐ Good (occasional JSON parse failures → fallback) |
| `google/gemini-2.0-flash` (paid) | ~$0.01/run | ⭐⭐⭐⭐⭐ Best (native structured output) |
| `gpt-4o-mini` (default) | ~$0.02/run | ⭐⭐⭐⭐⭐ Best (OpenAI is the default for a reason) |
| Disable memory entirely | Free | ❌ No cross-session recall |

---

### 9.5 Error #3: Embedding API Quota (429) — Google & OpenAI

**What happened:**
```
429 RESOURCE_EXHAUSTED - models/embedding-001 quota exceeded
```

**Root Cause:**
The `Memory` class needs an **embedder** to convert text to vectors for similarity search. The defaults (`text-embedding-3-small` for OpenAI, `embedding-001` for Google) require API keys and have rate limits.

**The Fix — `_hash_embedder` (Zero API, Zero Cost):**
```python
def _hash_embedder(texts: list[str], *, dim: int = 3072) -> list[list[float]]:
    """Deterministic embedding via SHA256 — no API calls."""
    vectors = []
    for t in texts:
        buf = b""
        i = 0
        payload = t.strip().encode("utf-8", errors="ignore")
        while len(buf) < dim * 4:
            buf += hashlib.sha256(payload + f"|salt-{i}".encode("ascii")).digest()
            i += 1
        buf = buf[: dim * 4]
        floats = list(struct.unpack(f"<{dim}f", buf))
        norm = sum(x * x for x in floats) ** 0.5
        floats = [x / norm for x in floats] if norm > 1e-9 else [0.0] * dim
        vectors.append(floats)
    return vectors
```

> [!WARNING]
> **Trade-off:** Hash-based embeddings are **deterministic but not semantic**. The word "dog" and "puppy" will have completely different vectors. This means recall accuracy is lower than real embedding models. For cross-session memory where you're storing exact task outputs, this is acceptable. For nuanced semantic search, use a real embedder.

**Alternatives for Embeddings:**

| Embedder | Semantic Quality | API Needed? | Setup |
| :--- | :--- | :--- | :--- |
| `_hash_embedder` (SHA256) | ⭐ Exact match only | ❌ No | Zero config |
| `fastembed` (local) | ⭐⭐⭐⭐ Good | ❌ No | `pip install fastembed` |
| `sentence-transformers/all-MiniLM-L6-v2` | ⭐⭐⭐⭐ Good | ❌ No | HuggingFace local |
| Google `embedding-001` | ⭐⭐⭐⭐⭐ Best | ✅ Yes | `GOOGLE_API_KEY` |
| OpenAI `text-embedding-3-small` | ⭐⭐⭐⭐⭐ Best | ✅ Yes | `OPENAI_API_KEY` |

---

### 9.6 Warning: `Invalid type Memory for attribute 'crew_memory'`

**What it is:**
```
Invalid type Memory for attribute 'crew_memory' value. Expected one of ['bool', 'str', 'bytes', 'int', 'float']
```

**Root Cause:**
This comes from **OpenTelemetry's tracing layer** inside CrewAI. When the crew starts, the trace listener tries to log `span.set_attribute("crew_memory", <Memory object>)`. OpenTelemetry span attributes only accept primitive types (bool, str, int, float) — not Python objects.

**Impact:** ✅ **Zero**. Purely cosmetic. Memory works correctly.

**Fix:** Set `tracing=False` in the Crew constructor:
```python
Crew(memory=memory, tracing=False)
```

---

### 9.7 Warning: `Memory extraction failed, storing full content as single memory`

**What it is:**
```
WARNING:crewai.memory.analyze:Memory extraction failed, storing full content as single memory: Expecting value: line 1 column 1 (char 0)
```

**Root Cause:**
The `_PlainJsonLLM` wrapper asks DeepSeek to return JSON in plain text. Sometimes DeepSeek returns explanatory prose instead of raw JSON, or returns an empty string. `json.loads()` fails on these responses.

**Impact:** ✅ **Minimal**. CrewAI's fallback stores the **entire content as one memory** instead of splitting it into discrete facts. The memory is still saved — just not as granularly categorized.

**To eliminate this warning entirely:**
- Use a model that reliably returns JSON: `gpt-4o-mini` or paid `google/gemini-2.0-flash`
- Or accept the fallback (recommended for free-tier usage)

---

### 9.8 The Final Working Configuration

```python
from crewai.memory import Memory

class _PlainJsonLLM:
    """Forces DeepSeek into plain-text JSON mode to avoid response_format 400 errors."""
    def __init__(self, model: str):
        from crewai.llm import LLM
        self._inner = LLM(model=model)
    def supports_function_calling(self) -> bool:
        return False
    def call(self, messages, **kwargs):
        kwargs.pop("response_model", None)
        return self._inner.call(messages, **kwargs)
    def __getattr__(self, name):
        return getattr(self._inner, name)

def _hash_embedder(texts, *, dim=3072):
    """Local SHA256-based vectors — zero API quota usage."""
    # (see crew.py for full implementation)

memory = Memory(
    llm=_PlainJsonLLM("deepseek/deepseek-chat"),  # No 400 errors
    embedder=_hash_embedder,                        # No 429 errors  
    storage="./memory",                             # Local LanceDB
)

Crew(
    memory=memory,
    tracing=False,  # Suppresses crew_memory type warning
)
```

### 9.9 Warning: `Memory save analysis failed: extra_forbidden`

**What it is:**
```
WARNING:crewai.memory.analyze:Memory save analysis failed... 1 validation error for MemoryAnalysis: extracted_metadata.tools_mentioned: Extra inputs are not permitted
```

**Root Cause:**
This is the "Intelligence Overload" error. Using **DeepSeek** as the memory LLM means it is often *more* intelligent than the default OpenAI instructions expected. It correctly identifies tools like `Claude Code` and `n8n` in the research and tries to add a `tools_mentioned` field to the memory metadata. However, CrewAI's internal Pydantic model for memory analysis is set to `extra='forbid'`, so it rejects the extra intelligence.

**Impact:** ✅ **Zero**. CrewAI simply falls back to storing the result without the extra metadata tags. The core memory is still persisted. 

> [!TIP]
> This error specifically confirms that your **DeepSeek Memory Wrapper is working perfectly** — it's extracting high-value technical data, even if the base CrewAI framework isn't quite ready to categorize it yet!

> [!TIP]
> **Upgrade Path:** When you get a paid Google AI API key or OpenAI key, replace the `_PlainJsonLLM` with `"google/gemini-2.0-flash"` and the `_hash_embedder` with `{"provider": "google", "config": {"model": "models/embedding-001"}}` for maximum memory intelligence.

---

## 10. The "Runaway Agent" Stabilization (April 2026)

This section documents a critical stabilization effort that happened during a live run with the query `"government companies in tn 2026"`. The scout agent made **50+ Serper API calls** before completing — completely out of control. Here is the full root cause analysis and every fix applied.

---

### 10.1 Bug #1: Hardcoded AI Tool-Stack Mandate in `agents.yaml`

**Symptom observed:**
While researching traditional Tamil Nadu government PSUs (like TANGEDCO and TNRDC), the agent was sending searches like:
```
"Tamil Nadu Road Development Corporation" AI tools technical stack 2026
"TANGEDCO" Claude Code n8n automation 2026
```
These obviously returned zero results, so the agent tried 2-3 alternative queries per company, creating a cascading search explosion.

**Root Cause — `agents.yaml` (market_scout goal):**
```yaml
# BUG: Hardcoded, unconditional mandate
goal: >
  Research and identify the top 10-15 trending companies in the {industry} sector.
  You must EXPLICITLY search for agencies using every tool mentioned in the tech stack list.

backstory: >
  You are a technical market scout... If a user lists specific tools (like Claude Code,
  Codex, or OpenClaw), you ensure that your research specifically validates the use
  of those tools in the companies you find.
```
The agent's goal hardcoded this tech-tool validation for **every** industry, including traditional ones like government infrastructure, renewable energy, etc.

**The Fix — Industry-Adaptive Goal:**
```yaml
# FIXED: Conditional, industry-aware instructions
goal: >
  Research and identify the top 10-15 trending companies in the {industry} sector.
  Be EFFICIENT with your searches — consolidate queries and avoid redundant calls.
  Use no more than 10-15 total search calls to complete your research.

backstory: >
  You are an elite market scout who adapts your research strategy to the industry.
  For AI/tech sectors: validate companies' technical DNA (tools like Claude Code, n8n, OpenClaw).
  For traditional sectors (government, infrastructure, energy): focus on market dominance,
  revenue scale, policy tailwinds, and operational excellence. You are efficient —
  you batch your research into broad queries first, then do targeted deep-dives only
  on the top 3-5 most promising leads. You NEVER waste search calls on dead-end queries.
```

> [!IMPORTANT]
> **Key Lesson:** Agent `goal` and `backstory` fields in `agents.yaml` are LLM instructions. They carry the **same weight** as system prompts. Hardcoding tool-specific searches in the backstory makes the agent follow those instructions for every single run, regardless of the topic. Always make these conditional.

---

### 10.2 Bug #2: Hardcoded Mandate Duplicated in `tasks.yaml`

The same "MANDATORY" tool search instruction existed **twice** — in `agents.yaml` AND in `tasks.yaml`'s `scout_task`.

**Root Cause — `tasks.yaml` (scout_task description):**
```yaml
# BUG: Hardcoded MANDATORY instruction in task
scout_task:
  description: >
    ...
    MANDATORY: You must EXPLICITLY search for and verify the use of the specific
    tools mentioned (e.g. Claude Code, Codex, Gemini CLI, n8n, OpenClaw, etc.).
```

**The Fix — Conditional Task Instruction:**
```yaml
# FIXED: Industry-conditional
scout_task:
  description: >
    ...
    TECHNICAL DNA AUDIT: If the {industry} is AI or high-tech related, EXPLICITLY
    search for and verify the use of specific agentic tools (e.g. Claude Code,
    n8n, OpenClaw, Gemini CLI, etc.) as a proxy for efficiency. For traditional
    sectors, focus on regional market dominance and operational excellence.
```

> [!TIP]
> **Multiplier Effect Explained:** The reason 15 companies → 50+ searches is a simple multiplication:
> - 15 companies found × 3 queries each (primary, retry, retry-2) = **45+ searches**
> - Each failed AI tool search triggers the agent to retry with different keywords
> - With MANDATORY in both agents.yaml AND tasks.yaml, the instructions double-reinforced the bad behavior

---

### 10.3 Bug #3: No `max_iter` Cap on the Market Scout

Even with better instructions, an LLM can still decide to "try one more search." Without a hard code-level limit, runaway behavior is always possible.

**Root Cause — `crew.py` (market_scout agent definition):**
```python
# BUG: No limit — agent can loop forever
@agent
def market_scout(self) -> Agent:
    return Agent(
        config=config,
        tools=[SerperDevTool(), PushNotificationTool()],
        allow_delegation=False,
        verbose=True,
    )
```

**The Fix — Hard Cap via `max_iter`:**
```python
# FIXED: Hard-capped at 15 iterations max
@agent
def market_scout(self) -> Agent:
    return Agent(
        config=config,
        tools=[SerperDevTool(), PushNotificationTool()],
        max_iter=15,   # ← HARD LIMIT: cannot exceed 15 tool calls regardless of LLM decisions
        allow_delegation=False,
        verbose=True,
    )
```

> [!IMPORTANT]
> **`max_iter` vs. prompt instructions:**
> - **Prompt instructions** (in `agents.yaml` goal/backstory): The LLM *tries* to follow, but can "forget" under complex reasoning.
> - **`max_iter`** (in `crew.py`): A **programmatic hard limit** enforced at the CrewAI framework level. The agent physically cannot execute more than `max_iter` iterations. Always use both as belt-and-suspenders.

---

### 10.4 Bug #4: Output Routing — Files Saved to Wrong Folder

**Symptom:** Every run overwrote the same 4 files in the root `output/` folder. No per-run history was preserved.

**Root Cause 1 — `tasks.yaml` (static output paths):**
```yaml
# BUG: Static paths hardcoded in tasks.yaml
scout_task:
  output_file: output/market_intelligence.json   # ← always overwrites the same file!

financial_analysis_task:
  output_file: output/financial_audit.md

investment_recommendation_task:
  output_file: output/investment_recommendation.md
```

**Root Cause 2 — `crew.py` (missing dynamic path for financial/investment tasks):**
```python
# BUG: financial and investment tasks had NO output_file set in crew.py
# so they fell back to the static paths in tasks.yaml

@task
def financial_analysis_task(self) -> Task:
    return Task(config=self.tasks_config['financial_analysis_task'])
    # No output_file → uses tasks.yaml's static "output/financial_audit.md"

@task
def investment_recommendation_task(self) -> Task:
    return Task(config=self.tasks_config['investment_recommendation_task'])
    # No output_file → uses tasks.yaml's static "output/investment_recommendation.md"
```

**The Fix — Dynamic routing in `crew.py` + Remove static paths from `tasks.yaml`:**

Step 1: Remove all `output_file` lines from `tasks.yaml` (for financial/investment tasks).
Step 2: In `crew.py`, override with `self.output_dir` for ALL tasks:

```python
# FIXED: self.output_dir is computed from the topic slug in __init__
# e.g., for topic "government companies in tn", output_dir = "output/governemtn-companies-in-tn"

@task
def financial_analysis_task(self) -> Task:
    return Task(
        config=self.tasks_config['financial_analysis_task'],
        output_file=f'{self.output_dir}/financial_audit.md'     # ← dynamic!
    )

@task
def investment_recommendation_task(self) -> Task:
    return Task(
        config=self.tasks_config['investment_recommendation_task'],
        output_file=f'{self.output_dir}/investment_recommendation.md'  # ← dynamic!
    )
```

> [!IMPORTANT]
> **Why the fix only applies on the next run:** In the Tamil Nadu government run, the bugs were patched mid-execution (while the old process was still running). Because Python loads the source code **once at startup**, the running process used the old, buggy code. The fixes only took effect on the next `uv run stock_picker_me run`.

---

### 10.5 The "Active-Run Patch" Problem

This is a general principle when debugging long-running agentic processes:

| Scenario | Does the fix apply? |
| :--- | :--- |
| You edit `agents.yaml` while a run is in progress | ❌ No — config is loaded at startup |
| You edit `crew.py` while a run is in progress | ❌ No — Python bytecode is already loaded |
| You edit `tasks.yaml` while a run is in progress | ❌ No — CrewAI reads it at startup |
| You stop the run and start a new one | ✅ Yes — all changes take effect |

> [!TIP]
> Always **kill (`Ctrl+C`) and restart** after applying code changes. Never assume a running process will pick up live edits.

---

### 10.6 Summary: All Fixes Applied in Session 2

| File | Change | Impact |
| :--- | :--- | :--- |
| `agents.yaml` (market_scout goal) | Removed hardcoded MANDATORY AI tool search | Prevents 50+ searches for non-tech industries |
| `agents.yaml` (market_scout backstory) | Made tool validation industry-conditional | Agent adapts behavior to the topic |
| `agents.yaml` (financial_researcher) | Removed AI tool cross-reference mandate | Financial agent focuses on fundamentals for traditional sectors |
| `tasks.yaml` (scout_task) | Changed MANDATORY → conditional TECHNICAL DNA AUDIT | Preserves tech-stack validation for AI industries |
| `tasks.yaml` (financial/investment tasks) | Removed static `output_file` paths | Forces crew.py to control routing |
| `crew.py` (market_scout agent) | Added `max_iter=15` | Hard cap on tool calls regardless of LLM behavior |
| `crew.py` (financial_analysis_task) | Added `output_file=f'{self.output_dir}/financial_audit.md'` | Routes to per-run subfolder |
| `crew.py` (investment_recommendation_task) | Added `output_file=f'{self.output_dir}/investment_recommendation.md'` | Routes to per-run subfolder |
