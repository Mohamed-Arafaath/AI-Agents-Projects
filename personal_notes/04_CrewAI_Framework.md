# Chapter 4: Multi-Agent Collaboration (CrewAI)

While the OpenAI SDK is **Developer-First** (focusing on granular tool and handoff logic), CrewAI is **Role-First**. It shifts the focus from "How do I code this?" to "How do I manage this team?"

---

## 1. The Role-Based Philosophy
In CrewAI, you don't just define an agent; you define a **Persona**. Every agent has a `role`, a `goal`, and a `backstory`. This provides a rich context that guides their behavior without needing massive system prompts for every call.

---

## 2. Professional Project Setup: The `uv` Way
Modern CrewAI projects are built as **UV projects**. This ensures lightning-fast dependency management and isolated environments for your agents.

### Installation & Initialization
```bash
# 1. Install CrewAI as a global tool using uv
uv tool install crewai

# 2. Create a new crew project structure
crewai create crew my_crew

# 3. Running the crew project
crewai run
```

### The "Opinionated" Directory Structure
When you run `create crew`, the framework builds a production-ready folder hierarchy. This is where the "Expert" logic resides:

```text
my_crew/
├── src/
│   └── my_crew/
│       ├── config/
│       │   ├── agents.yaml  # <--- Define Agent Personas here
│       │   └── tasks.yaml   # <--- Define Task Objectives here
│       ├── crew.py          # <--- The "Glue" connecting everything
│       └── main.py          # <--- Entry point for execution
```

> [!IMPORTANT]
> **YAML-Driven Development:**
> In professional CrewAI setups, you typically **don't** hardcode prompts in Python. You define them in `agents.yaml` and `tasks.yaml`. This allows non-technical stakeholders to tweak personalties and goals without touching the code.

---

## 3. The Architecture of "Magic": Decorators
CrewAI uses Python decorators to "glue" your team together. These are **Wrappers** that give your functions extra powers.

### @agent: The Registration
Tells the framework, "This method defines an official member of the team." It ensures the agent is registered with the Crew and available for tasks.

### @task: The Goal
Defines a specific unit of work. In CrewAI, a task is almost its own entity, containing:
- **Description:** What needs to be done.
- **Expected Output:** What the final result should look like.
- **Agent:** Who is responsible for it.

### @crew: The Coordinator
This is the "Captain" of the team. It automatically finds all methods decorated with `@agent` and `@task` within a class and connects them into a functional workflow.

---

## 3. Comparison: OpenAI SDK vs. CrewAI

| Feature | OpenAI SDK | CrewAI |
| :--- | :--- | :--- |
| **Mental Model** | Flowchart (Explicit) | Management (Implicit) |
| **Logic** | Manual Handoffs | Autonomous Collaboration |
| **Tooling** | `@function_tool` (Translator) | Self-managed Tools |
| **Analogy** | A Precision Scalpel | A Self-Driving Bus |

---

## 4. When to Use Which? (Agency Blueprint)

### Use the OpenAI SDK when:
- You need **absolute control** over every token and tool call.
- You are integrating with strict software systems (CRMs, SQL).
- You want a lightweight system with minimal dependency bloat.

### Use CrewAI when:
- You are simulating a **complex team** (e.g., a Marketing Department, a Research Lab).
- You want agents to **collaborate autonomously** with minimal code.
- You are building a system focused on **creative output** or high-level reasoning.

---

---
 
 ## 5. Technical Standards & Troubleshooting
 
 During the implementation of real-world crews (like **DebateMe**), several non-obvious technical standards emerged.
 
 ### The Environment Constant: Uppercase Keys
 Frameworks like CrewAI and LiteLLM rely on standard environment variable names. While Python is case-sensitive, these frameworks specifically look for **UPPERCASE** keys.
 - **INCORRECT:** `deepseek_api_key=sk-...` (Might not be detected by framework internals).
 - **CORRECT:** `DEEPSEEK_API_KEY=sk-...`
 
 ### The Configuration Bridge: `model` vs `llm`
 There is often a mismatch between course examples (which use `model=`) and the CrewAI framework (which uses `llm:` in YAML).
 - **Pro-Tip:** If your YAML uses `model:`, implement a local bridge in `crew.py` to ensure compatibility:
 ```python
 @agent
 def my_agent(self) -> Agent:
     config = self.agents_config['my_agent'].copy()
     if 'model' in config:
         config['llm'] = config.pop('model') # Map custom key to framework key
     return Agent(config=config, verbose=True)
 ```
 
 ### Workspace Execution
 When using `crewai run`, ensure you are in the directory containing the `pyproject.toml` file. The framework will automatically handle the virtual environment and dependency isolation.
 
 ---
 
 > [!TIP]
 > **Agency Pro-Tip: Sequential Output Management**
 > You can pipe the output of each sequential task into specific files (e.g., `output/propose.md`). This creates a "Paper Trail" of the AI's reasoning steps, which is invaluable for client reviews.
