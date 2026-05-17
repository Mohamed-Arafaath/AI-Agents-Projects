# CrewAI Lead Generation Pipeline — F&B Client Project

## Overview
Converted the entire n8n-based lead generation workflow (11 workflows: W1-W8, A1-A3) into a CrewAI agent-based pipeline. This is for the "Lead Generation Dubai Retail" Fiver client project under N8N Projects.

## Architecture

### Directory Structure
```
N8N Projects - Fiver/Lead Generation Dubai Retail (26-04-2026)/
└── crewai_agents/
    ├── config/
    │   ├── agents.yaml      # 10 CrewAI agents with tools + llm
    │   └── tasks.yaml        # 9 task definitions
    ├── tools/
    │   ├── search_tools.py   # SerperSearchTool, TavilySearchTool
    │   ├── web_tools.py      # WebScrapeTool, EmailExtractTool, JinaScrapeTool
    │   └── ai_tools.py       # DeepSeekChatTool, CompanyExtractTool, PersonFindTool
    ├── config_loader.py      # load_dotenv() + YAML → Agent/Task objects
    ├── email_scrapper_crew.py  # A3 hierarchical crew (tested, working)
    ├── lead_gen_crew.py       # Full 6-stage sequential pipeline
    ├── output/                # CSV outputs directory
    ├── pyproject.toml         # uv dependencies
    └── uv.lock                # locked versions
```

### Pipeline Stages (Sequential)
1. **Lead Sourcing** (W1) — Iterative Google search via Serper + DeepSeek extraction
2. **Company Research** (W3) — Tavily search + DeepSeek profile generation
3. **Find People** (★) — Serper + DeepSeek for decision-maker discovery
4. **Person Profile** (W4) — Jina LinkedIn scrape + Tavily + DeepSeek summaries
5. **Findings** (W5) — Pain point analysis → MysteryShoppers.ae solutions
6. **Cold Emails** (W6) — Personalized email generation with template

### Key Design Decisions
- **YAML-driven config**: agents.yaml defines all 10 agents (role, goal, backstory, tools, llm); tasks.yaml defines all 9 tasks
- **config_loader.py** handles YAML loading + load_dotenv() (UV guide pattern) + CrewAI object instantiation
- **Date-aware searching**: All queries include 2026; research prompts request reverse-chronological accomplishments (Q1 2026 → Q2 2026)
- **Output**: All CSVs saved to `output/` subdirectory with 22 fields
- **LLM**: deepseek/deepseek-v4-flash (CrewAI litellm format)
- **Package management**: uv (ultra-fast), confirmed at crewai v1.14.3

### A3 Email Scrapper
- Hierarchical sub-crew with manager coordinating search→scrape→extract
- Tested successfully: found 15-17 unique emails per query from 9 pages
- Uses SerperSearch + WebScrape (Jina AI + fallback) + regex email extraction

### API Dependencies
- DeepSeek (chat completions)
- Serper (Google search)
- Tavily (AI-optimized web search)
- Jina AI (web page text extraction)
- No Apollo/Apify token needed (replaced with Serper + DeepSeek)

### Dynamic Parallel Execution (within each stage)
- Each stage that iterates over leads uses `_run_parallel()` helper with `ThreadPoolExecutor`
- Dynamically splits leads into chunks: for 20 leads → 4 chunks × 5; for 100 leads → 10 chunks × 10
- Each chunk is processed by a separate worker thread with its own tool instances (no shared state)
- All chunks run concurrently, results merge automatically when all workers complete
- Stages still execute sequentially (Sourcing → Research → People → Profile → Findings → Emails)
- Max 8 concurrent workers by default, configurable via `max_workers` parameter

### Date Context & Reverse-Chronological Achievements
- `DATE_CONTEXT` global object computes current year/quarter/month at runtime
- All search queries include current year (2026) suffix for time-relevant results
- **Company research**: Extracts ALL accomplishments, milestones, expansions in reverse chronological order (newest first). Dedicated `Accomplishments (recent→old)` field in profile output
- **Person research**: Scrapes LinkedIn + web for ALL achievements, awards, promotions from most recent → oldest across entire career with approximate dates/quarters
- **Findings**: Pain point analysis based on `current_quarter_label` context
- **Cold emails**: Opening paragraph references a SPECIFIC recent accomplishment from previous/current quarter (e.g., "congratulations on the Q1 2026 expansion...")

### Scaling Lead Sourcing
- `stage_lead_sourcing` is fully iterative: keeps searching with varied queries until target hit or exhausted
- 20 query templates + AI-generated queries for deeper discovery using DeepSeek
- Excludes already-found company names in subsequent queries to surface new ones
- Results scale to 50-100+ leads (depends on market size)

## Updates — 2026-04-27

### Switched to Local Ollama (No More Paid API)
- **LLM**: `deepseek/deepseek-v4-flash` → `ollama/qwen3-8b-local` (5 GB, ~5s per call, 100% free)
- `agents.yaml` — all 10 agents updated to use local model
- `config_loader.py` — imports `LLM` from CrewAI; detects `ollama/` prefix and creates `LLM(model, base_url="http://localhost:11434")` to bypass CrewAI v1.14.3's buggy env var routing
- Installed `langchain-openai` dependency
- Tested: Agent + Task execution works correctly via local Ollama

### Phone Number Enrichment (Aggressive)
- Added `_extract_phones()` helper: regex for `tel:` links, UAE mobile (05X, +971), international formats with 7-15 digit validation
- **3-phase phone search** in enrichment stage:
  1. Tavily + Serper + page scrape (targeted queries)
  2. Contact page scraping (`/contact`, `/contact-us`, `/about`, `/contents/contact_us`, `/connect`, `/reach-us`, `/support`, etc.)
  3. Deep search — yellowpages, directory sites, quoted + unquoted name variants for short names (e.g. "ADNH")
- Same 3-phase approach applied to email search
- Result: 12/12 leads populated with phone numbers from local enrichment

### New Features
- `--resume` flag: `uv run python lead_gen_crew.py --resume path/to/existing.csv` — skips all stages, runs enrichment only
- Removed `jobFunctions` and `logoUrl` from CSV output
- Fixed `--leads` argument: user's shell line breaks caused argparse default (5) — now documented as single-line requirement

### Output Cleaning & Summary
- Added `_clean()` helper — strips `<think>...</think>` and `<reasoning>...</reasoning>` tags from all LLM-generated fields (companyProfile, personProfile, Findings, cold email body/subject)
- Applied `_clean()` to all 4 text generation stages after parallel execution
- Final summary now shows both Email and Phone status columns



## NVIDIA API Migration — 2026-04-27

### Migration from Local Ollama to NVIDIA API
- **LLM Update**: `ollama/qwen3-8b-local` → `nvidia/qwen3-coder` (NVIDIA API with Qwen model)
- `agents.yaml` — all 10 agents updated to use NVIDIA API model
- `config_loader.py` — updated to support NVIDIA API with Qwen model
- Installed `crewai[litellm]` dependency for broad model support
- Tested: Agent + Task execution works correctly via NVIDIA API

## Output File Improvements — 2026-04-27

### Enhanced _clean() Function
- Updated the `_clean()` function to handle markdown headers and other unwanted characters
- Added removal of markdown headers (#, ##, ###, etc.) from output files
- Improved whitespace handling and formatting cleanup

## File Corruption Fix — 2026-04-27

### Symptom
- `lead_gen_crew.py` line 77: SyntaxWarning invalid escape sequence `\s`
- `_clean()` function body was injected into middle of `_run_parallel()` docstring (lines 77-84)
- File also had duplicate `_clean()` at line 1025

### Fix
1. Removed corrupted docstring junk from `_run_parallel()` (lines 77-84)
2. Restored proper docstring: "Split leads into chunks and process each chunk in parallel via thread pool. Dynamically scales..."
3. Moved `_clean()` to line 70 (before first use at line 302)
4. Removed duplicate `_clean()` at line 1025
5. Verified: `uv run python -c "import lead_gen_crew; print('Syntax OK')"` passes

## .env Key Discovery — 2026-04-27

- `config_loader.py` loads .env from `../../AI Agents Course/projects/agents/.env` (parent[3] path)
- That .env confirmed to have `NVIDIA_API_KEY=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`
- `.env` was NOT present in `crewai_agents/` directory
- **Fixed**: copied .env to `crewai_agents/.env` so `load_dotenv('.env')` finds it directly
- Verified: `os.getenv('NVIDIA_API_KEY')` now returns correct value

## W3–W7 Blank Output Issue — 2026-04-27 (UNRESOLVED)

### Symptoms
- W1 (Serper search): produces company names correctly ✓
- W3 (Company Research): blank fields
- W4 (Person Profile): blank fields
- W5 (Findings): blank fields
- W6 (Cold Email): blank fields
- W7 (Enrich): blank fields

### Root Cause Analysis
- **NVIDIA API**: confirmed working via direct Python test (`qwen/qwen3-coder-480b-a35b-instruct` returned "Hello!")
- **Agent LLM**: correctly configured to NVIDIA API via `config_loader.py`
- **BUT**: `DeepSeekChatTool` (ai_tools.py line 41) hardcodes Ollama model and calls Ollama directly at `http://localhost:11434/v1/chat/completions`
- W3/W4/W5/W6 stages use `DeepSeekChatTool` for AI generation — NOT the CrewAI agent LLM
- This means W3–W6 are calling Ollama, not NVIDIA API

### Key Distinction
- **CrewAI agent LLM** (via agents.yaml): `nvidia/qwen3-coder` — used when agents reasoning via CrewAI framework
- **DeepSeekChatTool**: hardcodes Ollama endpoint — used in stage_lead_sourcing (W1), stage_company_research (W3), stage_find_people, stage_person_research, stage_findings, stage_cold_emails

### User Instruction
- User explicitly stated: **stick to NVIDIA model only, do NOT switch to Ollama**
- All AI generation must route through NVIDIA API, not Ollama

### Status
- Diagnostic was interrupted before exact failure point found
- Blanks may be due to: wrong API endpoint in DeepSeekChatTool, missing .env at time of call, or something else
- Pipeline needs debugging to determine why stage-level AI calls produce empty output

### Solution
- Need to modify `DeepSeekChatTool` in `ai_tools.py` to use NVIDIA API
- Current implementation uses Ollama directly instead of NVIDIA API
- This will require updating the tool to use the NVIDIA API configuration instead of hardcoded Ollama calls
- Successfully updated `DeepSeekChatTool` to use NVIDIA API with Qwen model
- Modified `ai_tools.py` to replace Ollama calls with NVIDIA API calls
- Updated headers to include NVIDIA API key from environment variables
- Changed model from `qwen2.5:3b` to `qwen/qwen3-coder-480b-a35b-instruct`
- Updated endpoint from `http://localhost:11434/v1/chat/completions` to `https://integrate.api.nvidia.com/v1/chat/completions`
