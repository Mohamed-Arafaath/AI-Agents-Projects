# Claude Code Skills Guide

**Date:** 2026-04-25
**Location:** `/Users/apple/Library/CloudStorage/OneDrive-UniversityofPisa/Startup building/AI Agency Planning/AI Agents Course/personal_notes`

---

## Skill Priority Order

When multiple skills with the same name exist, Claude Code resolves them in this priority order (highest to lowest):

| Priority | Source | Path | Override Ability |
|:--------:|:-------|:-----|:-----------------|
| **1st** | Enterprise | Managed settings (settings.json) | ✅ Highest — managed by organization |
| **2nd** | Personal | `~/.claude/skills/` | ✅ User's home directory |
| **3rd** | Project | `<repo>/.claude/skills/` | ✅ Repository-local overrides |
| **4th** | Plugins | Installed plugins | ❌ Lowest — lowest precedence |

### How Priority Works in Practice

```
┌─────────────────────────────────────────────────────────┐
│  Priority 1: Enterprise (settings.json / managed)         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Priority 2: Personal (~/.claude/skills/)          │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  Priority 3: Project (.claude/skills/)       │  │  │
│  │  │  ┌─────────────────────────────────────────┐ │  │  │
│  │  │  │  Priority 4: Plugins (lowest)           │ │  │  │
│  │  │  └─────────────────────────────────────────┘ │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Example scenarios:**

| Scenario | Which Skill Wins? |
|:---------|:------------------|
| Personal skill + Project skill both named `project-notes` | **Personal** (`~/.claude/skills/`) |
| Project skill + Plugin skill conflict | **Project** (repo-local) |
| Enterprise settings override all | **Enterprise** (managed, unchangeable) |

> [!TIP]
> **Personal skills in `~/.claude/skills/` take precedence over project skills.** This means your home directory configuration wins over any repository-local skill.

> [!IMPORTANT]
> If a repository is cloned that contains a skill with the same name as your personal skill, **your personal skill wins** due to higher priority.

---

## What is a Skill?

A skill is a reusable prompt that Claude Code can execute. It appears in `/skills` list and can be triggered by:
- Slash command: `/skill-name`
- Natural language matching the `description` field

---

## Skill File Structure

Skills live in `~/.claude/skills/<skill-name>/` (global) or `<project>/.claude/skills/<skill-name>/` (project-specific).

### Required File: `SKILL.md`

```markdown
---
name: skill-name
description: When Claude should trigger this skill (be specific about triggers)
---

Instructions here...
```

### Optional Files
- `README.md` — Documentation
- `index.js` — Custom logic (advanced)

---

## SKILL.md Format Explained

```markdown
---
name: my-skill          # Unique name, lowercase with hyphens
description: Use when user asks to do X  # Triggers the skill
---

When doing X:
1. First step
2. Second step
```

**Frontmatter fields:**
| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Skill identifier |
| `description` | Yes | When to use (trigger matching) |

---

## Quick Start: Create a Skill

```bash
# 1. Create the folder
mkdir -p ~/.claude/skills/my-custom-skill

# 2. Create SKILL.md
touch ~/.claude/skills/my-custom-skill/SKILL.md

# 3. Edit with content (example):
```

```markdown
---
name: my-custom-skill
description: Use when user asks to create a greeting
---

When creating a greeting:
1. Ask for the user's name
2. Generate a friendly greeting message
```

---

## Skill Types

### 1. Simple Prompt Skill
Just `SKILL.md` with instructions:
```
~/.claude/skills/hello/SKILL.md
```
Best for: straightforward, linear tasks

### 2. Scripted Skill (Advanced)
Has `index.js` for custom logic:
```
~/.claude/skills/complex-task/
├── SKILL.md
└── index.js
```
Best for: complex interactions, API calls

---

## Example Skills

### Example 1: Meeting Notes
```markdown
---
name: meeting-notes
description: Use when user asks to take meeting notes or create a meeting summary
---

When taking meeting notes:
1. Ask for meeting title and attendees
2. Create notes in format:
   # Meeting: [Title]
   **Date:** YYYY-MM-DD
   **Attendees:** ...
   ## Agenda
   ## Discussion
   ## Action Items
3. Save to specified directory
```

### Example 2: Code Review
```markdown
---
name: code-review
description: Use when user asks to review code or do a code review
---

When reviewing code:
1. Identify the language/framework
2. Check for: security issues, performance problems, style inconsistencies
3. Provide actionable feedback
4. Suggest specific improvements
```

### Example 3: Project Checklist
```markdown
---
name: project-checklist
description: Use when user asks to create a checklist for a project or start a new project checklist
---

When creating a project checklist:
1. Ask for project name and type
2. Generate checklist with sections:
   - Setup
   - Development
   - Testing
   - Deployment
3. Save as `checklist_project-name.md`
```

---

## Testing Your Skill

### Method 1: Slash Command
Type `/my-custom-skill` in Claude Code prompt

### Method 2: Natural Language
Describe your need naturally:
> "I want to create meeting notes for today's standup"

### Method 3: Invoke via Skill Tool
Claude Code can call skills via the `Skill` tool

---

## Skill Best Practices

1. **Be specific with descriptions** — "Use when user asks to X" works better than vague triggers
2. **Keep instructions clear** — Numbered steps for clarity
3. **Use examples** — Include example input/output
4. **Match naming to purpose** — `meeting-notes` not `mn` or `notes`
5. **One skill, one purpose** — Don't bundle unrelated tasks

---

## Debugging Skills

| Problem | Solution |
|---------|----------|
| Skill not showing | Check `name` in frontmatter matches folder name |
| Wrong skill triggers | Refine `description` to be more specific |
| File not found | Verify path is `~/.claude/skills/` not elsewhere |

---

## Useful Paths

| Purpose | Path |
|---------|------|
| Global skills | `~/.claude/skills/` |
| Project skills | `<project>/.claude/skills/` |
| Settings | `~/.claude/settings.json` |
| Project settings | `<project>/.claude/settings.local.json` |

---

## Related Commands

```bash
# List all skills
ls ~/.claude/skills/

# Check skill content
cat ~/.claude/skills/<skill-name>/SKILL.md

# Remove a skill
rm -rf ~/.claude/skills/<skill-name>
```

---

## Calling Skills from Terminal

You can invoke Claude Code with a skill directly:

```bash
# Via claude code CLI
claude --print "/skill-name"

# Or run with skill pre-loaded
claude "(use /project-notes for MyProject)"
```

---

## Project Notes Skill

A special skill (`project-notes`) exists in this workspace for managing project documentation. See: `.claude/skills/project-notes/SKILL.md`

**When to use `/project-notes`:**
- User asks to create or find notes for a specific project
- User wants to update project documentation
- User asks to check existing notes

**How it works:**
1. Extracts project name from user request
2. Searches `personal_notes/` for existing notes (fuzzy matching)
3. If found → reports path and asks to open/append
4. If not found → creates new file with rich template

## Skill Priority Order

When multiple skills share the same name, Claude Code follows a specific precedence order to determine which one to execute. This allows for both organizational standards and individual customization.

| Priority | Level | Location | Purpose |
| :--- | :--- | :--- | :--- |
| **1 (Highest)** | **Enterprise** | Managed settings | Enforced standards for organizations. |
| **2** | **Personal** | `~/.claude/skills` | User-specific global skills available across all projects. |
| **3** | **Project** | `.claude/skills` (in repo) | Repository-specific skills shared with a team. |
| **4 (Lowest)** | **Plugins** | Installed plugins | Pre-packaged tools and community extensions. |

### Why this matters
- **Enforcement:** Organizations can ensure high-priority security or style checks (Enterprise) are never overridden by local project settings.
- **Customization:** If you find a repository has a "review" skill that doesn't fit your workflow, you can create a Personal version in `~/.claude/skills` with the same name, and your personal version will "win."
- **Conflict Avoidance:** To avoid accidental overrides, it is best practice to use descriptive names (e.g., `frontend-review` vs `backend-review`) instead of generic ones like `review`.

### Examples
1. **The Corporate Standard (Enterprise > Personal):**
   - Your company defines an Enterprise skill called `code-review` that enforces strict security rules.
   - You create a Personal skill also called `code-review` in your `~/.claude/skills` folder.
   - **Result:** When you run `/code-review`, the **Enterprise** version executes. You cannot override corporate policy with a personal skill of the same name.

2. **Personal Workspace Customization (Personal > Project):**
   - You clone a new open-source repository that has a Project-level skill called `project-notes` in its `.claude/skills` folder.
   - You already have your own `project-notes` skill (the one we built!) in your `~/.claude/skills` folder.
   - **Result:** When you run `/project-notes`, **your Personal version** executes. This allows you to maintain your preferred note-taking style across all projects you work on, regardless of what the repository provides.

---

*End of Guide*