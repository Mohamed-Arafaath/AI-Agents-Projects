# Chapter 8: StartupAnalyzerMe — Forensic Venture Intelligence

The **StartupAnalyzerMe** crew is a high-ticket "Venture Blueprint" engine. It is designed to identify "Hidden Gem" startups and reverse-engineer their operational DNA. This project demonstrates the **Dual-Engine Search Strategy** (Serper + Tavily).

---

## 1. The Core Insight: Idea vs. Founder
Most startup research tools are "Idea-First." They search for "Best AI ideas." This project is **"Founder-Market Fit" First**.

### The Moat: The Stakeholder Interview
Before the bot searches for a single startup, the `query_optimizer` initiates an elite-level "Stakeholder Interview." It ignores the user's initial prompt and probes 10+ dimensions:
- **Liquid Capital:** How much burn can the founder handle?
- **Regional Edge:** Does the user have an advantage in Bangalore vs. UAE?
- **Technical Edge:** What is the user's "Agentic Advantage"?

---

## 2. Technical Standard: Search Tiering (Cost vs. Depth)
One of the most advanced technical implementations in this course is the **Search Tool Hierarchy**. Using only deep search (Tavily) is expensive; using only snippets (Serper) is shallow.

### The Solution: The Tiered Custom Tool
1.  **Serper (The Workhorse):** Used for 90% of searches to find broad lists and LinkedIn profiles.
2.  **Tavily (The Surgeon):** A custom tool built in `tools/tavily_tool.py` that extracts **FULL page content** for the top 3 leads only.

### Custom Tool Implementation (`tavily_tool.py`):
```python
def _run(self, query: str) -> str:
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(
        query=query, 
        search_depth="advanced", # <--- Forces deep extraction, not just snippets
        max_results=5
    )
    # Extracts Page Content + Summaries
    return "\n".join([f"{r['title']}: {r['content']}" for r in response['results']])
```

---

## 3. Implementation Pattern: Dynamic Topic Slugs
To manage multiple research clients, the `main.py` entry point implements a **Dynamic Path Logic**.

```python
def generate_topic_slug(input_text):
    words = re.findall(r'\w+', input_text.lower())
    return "-".join(words[:4]) # Create "ai-agent-agency" slug

def run():
    topic_slug = generate_topic_slug(industry)
    # Initialize crew with a subfolder for ALL output files
    StartupAnalyzerMe(topic_slug=topic_slug).crew().kickoff()
```
- **The Magic:** This ensures that the research for a "Fintech App" never overwrites the files for an "eCommerce Bot." Everything is saved in `output/{topic_slug}/`.

---

## 4. The Forensic CTO Audit
The `technical_auditor` agent acts as a "Forensic CTO."
- **Goal:** Reverse-engineer the "Agentic Orchestration."
- **Method:** Analyze digital footprints (GitHub commits, Stripe integration mentions, niche forum sentiment) to deduce a competitor's *internal* unit economics.

---

## 5. Architectural Hierarchy & Tasks

| Task | Agent | Output File |
| :--- | :--- | :--- |
| **Refinement** | Query Optimizer | (Pause for Human Input) |
| **Discovery** | Startup Researcher | `dossier.json` |
| **Audit** | Technical Auditor | `forensic_audit.md` |
| **Blueprint**| Growth Mentor | `execution_playbook.md` |

---

## 6. Key Design Principles Learned
1.  **Search tiers save money.** Use Serper to "Sniff" and Tavily to "Bite."
2.  **Slugify your output.** Dynamic directory creation is a requirement for professional agencies.
3.  **Human Input is a Moat.** Forcing an "Elite Interview" in YAML makes the AI feel like a high-end partner rather than a low-end tool.
4.  **OSINT over Databases.** The best solo-founders stay off Crunchbase. Instruct your agents to find the "Hidden Trajectory."

---

> [!TIP]
> **Production Standard: `uv run` Entry Point**
> Never use `python3 src/main.py`. Always use the entry point defined in `pyproject.toml`:
> ```bash
> uv run startup_analyzer_me
> ```
> This ensures all environment variables and internal package references (like `startup_analyzer_me.tools`) are resolved correctly.
