# Chapter 6: DebateMe — Sequential Competitive Reasoning

The **DebateMe** project demonstrates how to use the CrewAI framework to simulate a structured intellectual competition. Unlike the template "Researcher" crew, this project focuses on **Sequential Argumentation** and **Synthesis**.

---

## 1. Architectural Blueprint: The Sequential Debate
The crew is built on a three-stage sequential process where each task's output provides the context for the next.

1.  **Propose Task**: The Proponent establishes the foundation by arguing in favor of the motion.
2.  **Oppose Task**: The Opponent (using the same debater agent) analyzes the proposal and provides a logically sound rebuttal.
3.  **Judging Task**: The Judge (a separate impartial agent) weighs both the proposal and opposition to deliver a final verdict.

---

## 2. Key Innovation: Single-Agent Multi-Role
A crucial learning from this project is that a single **Debater** agent can perform opposite roles within the same crew. 

- **The Pattern:** Instead of creating two separate agents for "Pro" and "Con", we defined one highly skilled "Debater" agent and assigned it to two separate tasks with opposing instructions.
- **Benefit:** Reduces configuration overhead and ensures a consistent quality of argumentation across both sides of the debate.

---

## 3. Dynamic Variables: The `{motion}` Pivot
In this implementation, we standardized the use of the `{motion}` variable across all agents and tasks.

- **Standardization:** By replacing the generic `{topic}` with `{motion}`, the personality of the agents shifts from "Data Researcher" to "Competitive Debator".
- **Implementation in `main.py`:**
```python
inputs = {
    'motion': 'There needs to be strict laws to regulate LLMs',
    'current_year': str(datetime.now().year)
}
```

---

## 4. Technical Wins: Configuration & Environment

### The "Model" Key Bridge
As documented in the framework notes, we implemented a custom bridge in `crew.py` to allow the user to use the `model:` key in their YAML files while maintaining framework compatibility.

```python
@agent
def debater(self) -> Agent:
    config = self.agents_config['debater'].copy()
    if 'model' in config:
        config['llm'] = config.pop('model') # Bridge to framework parameter
    return Agent(config=config, verbose=True)
```

### Output Standardisation
We used the `output_file` parameter in `tasks.yaml` to create a structured output directory.
- `output/propose.md`
- `output/oppose.md`
- `output/verdict.md`

---

## 5. Key Design Principles Learned

1.  **Variables drive Persona.** Changing a variable name (Topic -> Motion) can significantly improve the LLM's role-play quality.
2.  **Sequential tasks create context.** The "Oppose" task naturally receives the output of the "Propose" task, allowing for direct rebuttals.
3.  **Decisive Judging.** The judge's expected output should be forced into a "verdict" format to prevent it from simply repeating what the debaters said.
4.  **Always use Uppercase ENV keys.** `DEEPSEEK_API_KEY` is a hard requirement for LiteLLM/CrewAI to correctly identify the provider.
