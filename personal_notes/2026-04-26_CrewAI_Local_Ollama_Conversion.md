# Converting CrewAI from Cloud APIs (DeepSeek/OpenAI) to Local Ollama

This document outlines the exact steps required to migrate a CrewAI pipeline from a paid cloud API (like DeepSeek or OpenAI) to a completely free, local Ollama model.

## Step 1: Update your YAML Configuration
In your `agents.yaml` file, you need to change the `llm` parameter for every agent.
CrewAI natively recognizes the `ollama/` prefix.

**Before (Cloud DeepSeek):**
```yaml
llm: deepseek/deepseek-chat
```

**After (Local Ollama):**
```yaml
llm: ollama/qwen3-8b-local  # Or ollama/qwen2.5:14b
```

## Step 2: Update Python Code (The Base URL Fix)
In newer versions of CrewAI (v1.14+), relying on LiteLLM environment variables to route Ollama traffic often causes connection bugs (defaulting to `0.0.0.0/v1` instead of `localhost`). 

To fix this, you must explicitly pass the `base_url` directly into CrewAI's native `LLM` object inside your configuration loader (e.g., `config_loader.py`).

**The Fix:**
```python
from crewai import Agent, Task, LLM

# Inside your function that loads the YAML config (e.g., load_agents):
if "llm" in cfg:
    llm_str = cfg["llm"]
    if llm_str.startswith("ollama/"):
        # Explicitly create the LLM object for Ollama to bypass env var bugs
        agent_kwargs["llm"] = LLM(
            model=llm_str,
            base_url="http://localhost:11434"
        )
    else:
        # Fallback for standard cloud APIs
        agent_kwargs["llm"] = llm_str
```

## Step 3: Run the Local Server
Ensure that your Ollama server is running in the background before you start your CrewAI pipeline:
```bash
ollama serve
```

## Best Models for M1/M2 Mac (32GB RAM)
For agentic workflows requiring strict JSON output and tool-calling:
1. **qwen2.5:14b** - The "Sweet Spot". Very fast (~30 tokens/sec), excellent at tool-calling.
2. **qwen2.5:32b** - The "Smartest". Will use ~20GB of your RAM. Slower, but produces much higher quality research synthesis.
3. **qwen3-8b-local** (or equivalent 8B) - The "Fastest". ~5 seconds per response. Good for massive parallel processing where deep reasoning isn't as critical.
4. **deepseek-r1:14b** - Great for reasoning, but sometimes struggles with rigid CrewAI JSON structures.
