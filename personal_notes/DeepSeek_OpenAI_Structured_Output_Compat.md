# DeepSeek ↔ OpenAI Structured Output Compatibility

## The Problem

CrewAI's `output_pydantic` on tasks triggers OpenAI's `beta.chat.completions.parse()` (structured output API). DeepSeek's API rejects this:
```
Error code: 400 - {'error': {'message': 'This response_format type is unavailable now'}}
```

## Root Cause

- OpenAI has a dedicated `response_format` parameter for structured JSON output
- DeepSeek only supports `response_format: {"type": "json_object"}` in chat completions, NOT the beta structured output API
- CrewAI 1.12.x uses `self.client.beta.chat.completions.parse()` when `output_pydantic` is set on a Task
- There is no `supports_function_calling()` check in the task execution path (unlike the memory path which has this guard)

## The Solution

**Don't use `output_pydantic` on Task creation.** Instead:
1. Prompt the LLM to output JSON directly in the task description (with exact schema)
2. Parse the raw text output manually in `main.py` using Pydantic's `model_validate()`
3. DeepSeek supports `{"type": "json_object"}` via standard chat completions — no beta API needed

## Implementation Pattern

### 1. Task Description (YAML) — Embed exact JSON schema
```yaml
design_task:
  description: >
    ...requirements...
    You MUST return ONLY valid JSON matching this schema:
    {
      "module_name": "...",
      "class_name": "...",
      "methods": [{"name": "...", "params": [...], ...}],
      ...
    }
```

### 2. Task Creation (crew.py) — No output_pydantic
```python
def _task(description, expected_output, agent, context=None):
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context or [],
        # NO output_pydantic — DeepSeek doesn't support it
    )
```

### 3. Output Parsing (main.py) — Post-hoc JSON parsing
```python
def _try_parse_json(raw: str, model_class: type) -> object | None:
    # Strip markdown fences, try direct json.loads, fall back to regex extraction
    cleaned = raw.strip()
    cleaned = cleaned.removeprefix("```json\n").removesuffix("\n```")
    try:
        data = json.loads(cleaned)
        return model_class.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        # Try regex extraction as last resort
        import re
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return model_class.model_validate(json.loads(match.group(0)))
    return None
```

## Related Patterns

### `_PlainJsonLLM` for Memory LLM (from StockPickerMe)
Used when DeepSeek is the memory analysis LLM. Forces `supports_function_calling() -> False` so CrewAI takes the plain-text branch:
```python
class _PlainJsonLLM:
    def supports_function_calling(self):
        return False
    def call(self, messages, **kwargs):
        kwargs.pop("response_model", None)
        return self._inner.call(messages, **kwargs)
```

### `response_format: json_object` (from EngineeringTeamMe Phase 0)
Used in `_analyze_requirements()` — direct DeepSeek API call with `response_format={"type": "json_object"}`. This works because it's the standard chat completions API, not the beta structured output API.

## When to Use Each Approach

| Approach | When to Use |
| :--- | :--- |
| `response_format: json_object` | Direct API calls (not CrewAI) — use in `_analyze_requirements()` phase |
| Prompt-embedded JSON schema | CrewAI tasks with DeepSeek — avoid `output_pydantic` entirely |
| `_PlainJsonLLM` wrapper | DeepSeek as memory LLM — needs `supports_function_calling() -> False` |
| OpenAI native `output_pydantic` | Only when using OpenAI as the LLM provider |
