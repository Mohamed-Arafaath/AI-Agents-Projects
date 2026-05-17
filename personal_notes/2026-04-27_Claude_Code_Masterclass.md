# 📘 Claude Code A-Z Masterclass: Build & Sell (2026 Edition)

> **Reference:** Based on the 4-Hour Comprehensive Video Tutorial "CLAUDE CODE FULL COURSE 4 HOURS: Build & Sell".
> **Target Audience:** AI Agency Owners, Automation Engineers, and non-technical founders looking to build software pipelines.

---

## 📑 Masterbook Index

1. [Phase 1: Foundations & Setup](#phase-1-foundations--setup)
2. [Phase 2: Core Context Engineering (CLAUDE.md)](#phase-2-core-context-engineering-claudemd)
3. [Phase 3: Customizing the Agent (Skills & Hooks)](#phase-3-customizing-the-agent-skills--hooks)
4. [Phase 4: Advanced Integrations (MCP)](#phase-4-advanced-integrations-mcp)
5. [Phase 5: Teams & Context Management](#phase-5-teams--context-management)
6. [Phase 6: The 8 Agentic Hacks](#phase-6-the-8-agentic-hacks)
7. [Phase 7: Deployment & Monetization](#phase-7-deployment--monetization)
8. [Phase 8: Practical Builds](#phase-8-practical-builds)

---

## 🛠️ Phase 1: Foundations & Setup

### 1.1 What is Claude Code?
Claude Code is a CLI-based agentic coding companion. Unlike typical chat interfaces (like ChatGPT or standard Claude), Claude Code runs inside your terminal, meaning it has **direct access to your file system, bash environment, and git history**. It writes code, runs tests, fixes its own errors, and commits changes.

### 1.2 Installation
To install Claude Code globally, run:
```bash
npm install -g @anthropic-ai/claude-code
```

**Authentication:**
```bash
claude login
```
*Note: If you are using a local proxy (like Jan or Ollama) with OpenRouter/NVIDIA models, you configure `ANTHROPIC_BASE_URL` in your `.zshrc` to point to `127.0.0.1:1337/v1` to bypass official API costs.*

### 1.3 Pricing & API Tiers
*   **Direct API:** Pay-per-token. Highly recommended to use `claude-3-5-sonnet` for heavy lifting and `claude-3-haiku` for fast, cheap metadata scraping.
*   **Local/Proxy (2026 Meta):** Bypassing billing by running NVIDIA NIM or Jan local servers for free processing.

---

## 🧠 Phase 2: Core Context Engineering (CLAUDE.md)

The biggest mistake beginners make is treating Claude Code like a conversational AI. It is an **engineer**. Engineers need a spec sheet.

### 2.1 The Project Brain
`CLAUDE.md` is a magical file. If it exists in your root directory, Claude Code reads it automatically on launch. It serves as the unshakeable foundation for the AI's behavior.

**Best Practice Template for an AI Agency:**
```markdown
# AI Agency Architecture Rules

## 1. Identity
You are an elite Senior Full-Stack Developer and UI/UX expert.
You prioritize clean, modular code over quick hacks.

## 2. Tech Stack
- Frontend: HTML/CSS/Vanilla JS (No Tailwind unless specified)
- Design: Glassmorphism, GPU-accelerated animations (will-change)
- Backend: Python 3.12, N8N, CrewAI

## 3. Formatting Rules
- NEVER delete user comments.
- ALWAYS use specific tool calls (e.g., replace_file_content) instead of running `sed` via bash.
- Keep CSS variables at the top of `styles.css`.
```

---

## ⚙️ Phase 3: Customizing the Agent (Skills & Hooks)

### 3.1 Skills
Skills are reusable instructions you give Claude to perform repetitive tasks. You define them in a `.claude/skills/` directory.

**Example Skill: `format_seo.md`**
```markdown
# SEO Formatting Skill
When asked to "Format for SEO", you must:
1. Ensure there is only one <h1> tag.
2. Inject meta descriptions.
3. Add alt tags to all images.
```

### 3.2 Hooks (Event-Driven AI)
Hooks allow you to run scripts *before* or *after* Claude takes an action.

**Pre-commit Hook:**
Configure a hook to run ESLint or a Python linter before Claude is allowed to commit its code. If the linter fails, Claude intercepts the error and fixes its own code automatically.

---

## 🔌 Phase 4: Advanced Integrations (MCP)

**Model Context Protocol (MCP)** is the game-changer of 2026. It allows Claude Code to securely read databases, connect to GitHub, or inspect live Chrome instances without exposing API keys in plaintext.

### 4.1 Database MCP
Instead of hardcoding SQL credentials, you use an MCP server.
```json
// claude_config.json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/mydb"]
    }
  }
}
```
*Result:* Claude can now autonomously query the database to understand the data schema before writing backend code.

### 4.2 Browser/DevTools MCP
Allows Claude to "look" at the DOM of a running React or vanilla JS app and fix CSS bugs by reading the actual computed styles in the browser.

---

## 🛡️ Phase 5: Teams & Context Management

### 5.1 Context Rot
When a chat gets too long, the AI forgets earlier instructions. This is called Context Rot.
**Solution:** 
1. Use `/compact` frequently to compress the conversation.
2. Use `/clear` and rely on `CLAUDE.md` and external Markdown artifacts for memory.

### 5.2 Agent Teams (Worktrees)
As shown in previous setups, you can run multiple Claude Code instances in parallel using `git worktree`.
*   **Agent A:** Working on `backend.py`
*   **Agent B:** Styling `styles.css`
*   **Agent C:** Reviewing logs.

---

## 💡 Phase 6: The 8 Agentic Hacks

1. **The "Plan First" Rule:** Always force Claude to write an `implementation_plan.md` artifact before writing a single line of code.
2. **The "No Bash" Rule:** Force Claude to use `replace_file_content` instead of running `echo` or `sed` in the terminal to avoid formatting destruction.
3. **Skeleton UI First:** When building apps, have Claude generate the skeleton loading states *before* the API logic.
4. **The `/resume` Trick:** Use `claude --resume <ID>` to pick up a dropped session without losing context.
5. **Danger Mode:** Use `--dangerously-skip-permissions` for fully autonomous runs (only in sandboxed environments).
6. **Error Looping:** If a script fails, just type "fix it" and let Claude read the stderr directly.
7. **N8N Sync:** Use Claude Code to write Python scripts that trigger N8N webhooks.
8. **Git Checkpoints:** Tell Claude to "commit changes" after every successful function implementation.

---

## 🚀 Phase 7: Deployment & Monetization

For an AI Agency, the code is only valuable if it's deployed and sold.

1. **Vercel / Netlify:** For frontend dashboards (like the Web Banking App). Claude can automate the `vercel deploy` command.
2. **Modal / Railway:** For backend Python agents (like Lead Generation).
3. **Monetization (Build & Sell):**
    *   *SaaS:* Build a specific tool (e.g., a Mystery Shopper Questionnaire generator) and sell subscriptions.
    *   *Service Arbitrage:* Use the Lead Gen Crew to scrape emails, then use Claude Code to build custom landing pages for those leads automatically, charging a $500 setup fee.

---

## 🏗️ Phase 8: Practical Builds

### Build 1: YouTube Content Pipeline
*   **Goal:** Automate video research and script writing.
*   **Process:** 
    1. Claude Code uses `yt-dlp` to download transcripts.
    2. Uses an MCP connection to a Notion database to pull brand guidelines.
    3. Writes a 15-minute video script and saves it to `outputs/scripts/`.

### Build 2: Premium Website (Fintech Dashboard)
*   **Goal:** A high-end UI matching Stripe/Apple aesthetics.
*   **Process:**
    1. Define variables (Glassmorphism, cubic-bezier transitions) in `styles.css`.
    2. Write Vanilla JS with `requestAnimationFrame` for rolling counters.
    3. Use Claude Code to inject micro-interactions (ripple effects).

---

> **Final Takeaway for AI Agency:** Claude Code replaces the Junior Developer, the QA Tester, and the DevOps engineer. Your job is to be the **Product Manager**—managing the `CLAUDE.md` requirements and steering the workflow.
