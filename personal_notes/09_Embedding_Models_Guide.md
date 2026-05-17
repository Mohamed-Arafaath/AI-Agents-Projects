# 09: Understanding & Selecting Embedding Models

Embedding models are the "secret sauce" of AI memory. They convert text into mathematical vectors so the AI can find relevant memories based on meaning, not just exact keywords.

## Why `models/embedding-001`?

Currently, your project is using Google's models because:
1. **Zero Extra Cost:** It leverages your existing `GOOGLE_API_KEY`. 
2. **Reliability:** It is specifically optimized for retrieval tasks (RAG).
3. **Large Context:** It handles up to 3072 input tokens, perfect for storing detailed research summaries.
4. **Seamless Integration:** It works natively with the Google Generative AI stack you are already using.

---

## The Comparison: What are your options?

| Provider | Top Models | Best For... | Requirements |
| :--- | :--- | :--- | :--- |
| **Google** | `embedding-001`, `text-embedding-004` | Stability & large-scale usage. | `GOOGLE_API_KEY` |
| **OpenAI** | `text-embedding-3-small` | Industry-standard benchmarks. | `OPENAI_API_KEY` |
| **HuggingFace**| `all-MiniLM-L6-v2` | Privacy & high-speed local runs. | Local CPU/RAM usage |
| **Cohere** | `embed-english-v3.0` | Enterprise-grade retrieval accuracy. | `COHERE_API_KEY` |

---

## How to Select the Right Model

Follow this hierarchy of needs:

1. **Privacy First?** 
   - If yes, use a **Local HuggingFace** model. Your data never leaves your computer.
2. **Maximum Accuracy?** 
   - Use **OpenAI (Large)** or **Cohere**. These are the best at understanding deep context but cost the most.
3. **Balanced Intelligence & Cost (The "Elite" Sweet Spot)?** 
   - Use **Google**. It provides near-OpenAI performance while staying within your existing Google API ecosystem.
4. **Speed / Low Latency?** 
   - Use **OpenAI Small** or **HuggingFace**. These are optimized for millisecond-level retrieval.

---

### Implementation Snippet (Local / Privacy Mode)
To switch to a **Local HuggingFace model**, update the `embedder_config` in `crew.py` to:
```python
embedder_config = {
    "provider": "huggingface",
    "config": {
        "model": "sentence-transformers/all-MiniLM-L6-v2"
    }
}
```
This runs entirely on your local machine with zero API calls.

---

## When APIs Fail: The Zero-Cost `_hash_embedder` Pattern

### The Problem
During the StockPickerMe memory integration (April 2026), we hit **quota walls** on every cloud embedder:

| Provider | Error | Cause |
| :--- | :--- | :--- |
| Google `embedding-001` | `429 RESOURCE_EXHAUSTED` | Free tier daily limit hit |
| Google `text-embedding-004` | `404 Model not found` | Model name changed without notice |
| OpenAI `text-embedding-3-small` | Requires `OPENAI_API_KEY` | No key configured |

### The Solution: SHA256 Hash Embedder
A **dependency-free, zero-cost** embedding function that generates deterministic 3072-dim vectors from text using repeated SHA256 hashing:

```python
import hashlib, struct

def _hash_embedder(texts: list[str], *, dim: int = 3072) -> list[list[float]]:
    vectors = []
    for t in texts:
        buf, i = b"", 0
        payload = t.strip().encode("utf-8", errors="ignore")
        while len(buf) < dim * 4:
            buf += hashlib.sha256(payload + f"|salt-{i}".encode("ascii")).digest()
            i += 1
        floats = list(struct.unpack(f"<{dim}f", buf[:dim * 4]))
        norm = sum(x * x for x in floats) ** 0.5
        floats = [x / norm for x in floats] if norm > 1e-9 else [0.0] * dim
        vectors.append(floats)
    return vectors
```

### Trade-offs

| Feature | Hash Embedder | Real Embedder (Google/OpenAI) |
| :--- | :--- | :--- |
| **Semantic similarity** | ❌ None ("dog" ≠ "puppy") | ✅ Full |
| **API dependency** | ❌ None | ✅ Required |
| **Cost** | Free forever | Per-token pricing |
| **Speed** | <1ms | 50-200ms (network) |
| **Best for** | Exact recall, free-tier projects | Production semantic search |

> [!TIP]
> **The Hash Embedder is a "bridge" solution.** Use it when you're prototyping or your API quotas are exhausted. Upgrade to `fastembed` (local, semantic) or a cloud embedder when you need real semantic similarity.

### Updated Comparison Table

| Provider | Top Models | Semantic? | API Needed? | Best For... |
| :--- | :--- | :--- | :--- | :--- |
| **Hash (SHA256)** | `_hash_embedder` | ❌ | ❌ | Zero-cost prototyping |
| **FastEmbed** | `BAAI/bge-small-en-v1.5` | ✅ | ❌ | Local semantic search |
| **HuggingFace** | `all-MiniLM-L6-v2` | ✅ | ❌ | Privacy & local runs |
| **Google** | `embedding-001` | ✅ | ✅ | Google ecosystem |
| **OpenAI** | `text-embedding-3-small` | ✅ | ✅ | Industry standard |
| **Cohere** | `embed-english-v3.0` | ✅ | ✅ | Enterprise retrieval |

---

## Assigning Different Models Per Agent (Multi-Model Crews)

### Why?
Different agents have different cognitive needs. Reasoner models (slow, thorough) are expensive and slow but produce better structured designs. Chat models (fast, cheap) are sufficient for straightforward code output.

### DeepSeek Model Lineup

| Model String | DeepSeek Name | Type | Best For |
| :--- | :--- | :--- | :--- |
| `deepseek/deepseek-chat` | DeepSeek-V3 | Chat / Fast | High-throughput generation, straightforward coding |
| `deepseek/deepseek-reasoner` | DeepSeek-R1 | Reasoner / Slow | Complex planning, deep review, mathematical logic |

### Recommended Per-Agent Assignment Pattern

```yaml
# agents.yaml
code_planner:
  model: deepseek/deepseek-reasoner   # Design requires deep thinking

senior_coder:
  model: deepseek/deepseek-chat       # Code generation from clear blueprint = fast model

code_reviewer:
  model: deepseek/deepseek-reasoner   # Bug-finding requires deep reasoning
```

> [!NOTE]
> In `crew.py`, the agent factory must rename the `model` key to `llm` if the agents.yaml uses `model`:
> ```python
> config = self.agents_config['code_planner'].copy()
> if 'model' in config:
>     config['llm'] = config.pop('model')
> ```

---

## DeepSeek JSON Parsing Bug: `code_interpreter` Fix

### The Problem (Discovered April 2026)

When `allow_code_execution=True` is set on a CrewAI agent, the agent sends Python code to the `code_interpreter` tool via a JSON payload:
```json
{"code": "import numpy as np\n...400 lines of Python..."}
```
DeepSeek-V3 (and R1) frequently **fails to properly escape** newlines, quotes, and special characters in this massive JSON string, causing:
```
Error: Failed to parse tool arguments as JSON: Unterminated string starting at: line 1 column 62
```
The CrewAI framework catches this, feeds it back to the agent as an error, and the agent retries — **producing an infinite loop that burns 10 minutes of execution time before hitting the timeout.**

### The Fix: `parse_tool_call_args` Monkey-Patch

Instead of disabling code execution (which defeats the purpose of the autonomous coding pipeline), we monkey-patch CrewAI's internal `parse_tool_call_args` function to use a regex fallback when JSON parsing fails specifically for the `code_interpreter` tool:

```python
import crewai.utilities.agent_utils
import re, json

_original_parse = crewai.utilities.agent_utils.parse_tool_call_args

def _patched_parse_tool_call_args(func_args, func_name, call_id, original_tool=None):
    if isinstance(func_args, str) and func_name == "code_interpreter":
        try:
            return json.loads(func_args), None
        except json.JSONDecodeError:
            # Extract code block via regex even from broken JSON
            match = re.search(r'(?:"code"|\'code\')\s*:\s*["\'](.*)["\']\s*}?\s*$', func_args, re.DOTALL)
            if match:
                code_content = match.group(1)
                code_content = code_content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                return {"code": code_content}, None
    return _original_parse(func_args, func_name, call_id, original_tool)

crewai.utilities.agent_utils.parse_tool_call_args = _patched_parse_tool_call_args
```

Place this immediately after the Docker validation monkey-patch in `crew.py`.

### Trade-offs

| Approach | Code Execution | Timeout Risk | DeepSeek Compatible |
| :--- | :---: | :---: | :---: |
| `allow_code_execution=True` (vanilla) | ✅ | ❌ High (JSON loop) | ❌ |
| `allow_code_execution=False` | ❌ | ✅ None | ✅ |
| `allow_code_execution=True` + Patch | ✅ | ✅ Low | ✅ |

> [!TIP]
> The regex patch applies **only** to `code_interpreter`. All other tools follow normal JSON parsing. This is the safest and most targeted fix.
