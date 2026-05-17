# Web Engineering Crew & Claude CLI Tricks
**Date:** 2026-04-26
**Project:** Web Engineering Crew (CrewAI + DeepSeek V4)

## 1. The Claude CLI "God Mode" (Auto-Approve & Resume)
To run Claude Code completely autonomously without it constantly asking for `y/n` permissions, and to resume an exact previous session so you don't lose context, you can combine two powerful flags.

**The Command:**
```bash
claude --dangerously-skip-permissions --resume <SESSION_ID>
```
*   `--dangerously-skip-permissions`: Disables the security prompt for file edits, bash commands, and script execution. The agent runs in a fully autonomous loop.
*   `--resume <SESSION_ID>`: Picks up the exact terminal state, memory buffer, and context of a past chat.

## 2. Web Engineering Crew Architecture
We successfully cloned the `engineering_team_me` Python crew and repurposed it into a **World-Class Web Engineering Team**.

### Role Updates (`agents.yaml`):
*   **Creative UI/UX Director** (Lead) → Uses `deepseek-reasoner`
*   **Senior UI Developer** (HTML/Tailwind) → Uses `deepseek-v4-pro`
*   **Creative Interaction Engineer** (GSAP/Animations) → Uses `deepseek-v4-flash`
*   **Design QA** (Reviewer) → Uses `deepseek-reasoner`

### Structured Output (`models.py` & `tasks.yaml`):
Transitioned output expectations from Python modules to Web primitives:
*   `HtmlModule`
*   `CssModule`
*   `JsModule`

## 3. DeepSeek V4 API Compatibility Fixes (CRITICAL)
While setting up the Crew, we encountered several `400 Bad Request` and `Model Not Exist` errors from the DeepSeek API. We discovered and patched three major flaws in how CrewAI and LiteLLM handle DeepSeek V4.

### A. The `/v1` Base URL Crash
**The Problem:** LiteLLM (which CrewAI uses) defaults to appending `/v1` to custom API base URLs. However, DeepSeek's new V4 models (`v4-pro` and `v4-flash`) are hosted at the root URL, not the legacy `/v1` endpoint.
**The Fix:** Explicitly pass `base_url="https://api.deepseek.com"` (no `/v1`) directly into the `LLM()` constructor in `crew.py`.

### B. The "Model Not Exist" Crash
**The Problem:** The DeepSeek API servers do not recognize the strings `deepseek-v4-pro` or `deepseek-v4-flash`. They only accept `deepseek-chat` and `deepseek-reasoner`.
**The Fix:** We created an interceptor in `crew.py` that allows us to use "pro" and "flash" in `agents.yaml` for readability, but secretly translates them both to `deepseek-chat` before sending the request to the API.

### C. The Reasoning Content Crash
**The Problem:** DeepSeek's `reasoner` (R1) model crashes if it doesn't receive `reasoning_content` in multi-turn tool conversations.
**The Fix:** We mapped `deepseek-v4-pro` to the standard chat endpoint, which runs in **non-thinking mode**. For the Lead/Reviewer agents, we manually passed `extra_body={"thinking": {"type": "enabled"}}` to the LLM config so they can think without crashing the tool-using agents.

### D. The Pydantic Drop Bug
**The Problem:** `tasks.yaml` specified `output_pydantic: HtmlModule`, but the custom `_task` factory in `crew.py` ignored it, causing the agents to output raw text instead of strict JSON.
**The Fix:** Updated `crew.py` to parse the string from YAML, look it up in a `_PYDANTIC_MODELS` dictionary, and inject the actual Python class into the `Task(output_pydantic=...)` constructor.
