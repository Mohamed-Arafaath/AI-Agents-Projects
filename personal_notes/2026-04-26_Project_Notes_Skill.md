# Project Notes Skill

**Date:** 2026-04-26

## 1. Project Overview

A multi-file Claude Code skill that automates creation and management of project-specific documentation within the AI Agents Course workspace. It provides a standardized workflow for documenting projects with fuzzy search, rich templates, and structured output.

**Core Purpose:** Replace manual note-taking with an automated skill that searches existing notes, applies formatting templates, and maintains consistent documentation structure across all projects.

---

## 2. Technical Architecture

### The Core Components

| Component | Purpose | Key Feature |
| :--- | :--- | :--- |
| **SKILL.md** | Main instructions and workflow | Controls skill behavior, restricts tools |
| **assets/rich-template.md** | 8-section documentation template | Standardized project note structure |
| **references/priority-guide.md** | Skill precedence reference | Enterprise > Personal > Project > Plugins |
| **README.md** | Skill overview | Explains structure and key features |

### Skill Metadata

```yaml
---
name: project-notes
description: Manage and search project notes in the AI Agents Course folder. Triggers on requests like "create notes," "find project docs," "update documentation," or "record progress."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
model: sonnet
---
```

### Directory Structure

```
project-notes/
├── SKILL.md                    # Main entry point (1818 bytes)
├── README.md                   # Skill documentation (841 bytes)
├── assets/
│   └── rich-template.md        # 8-section template (959 bytes)
└── references/
    └── priority-guide.md        # Skill priority reference (2924 bytes)
```

---

## 3. Implementation Details

### Step 1: Workflow Initialization

When invoked, the skill follows this sequence:

```
1. Extract Project Name → 2. Search personal_notes/ → 3. Handle Found/New → 4. Create/Update
```

**Example trigger:**
- Slash command: `/project-notes`
- Natural language: "create notes for Email CRM Agent"

### Step 2: Fuzzy Search Pattern

Searches `personal_notes/` with case-insensitive matching:

```python
# Example: "Email CRM Agent" matches:
# - "Email CRM Agent.md"
# - "email_crm_agent.md"
# - "2026-04-25_Email_CRM_Agent.md"
```

### Step 3: Rich Template Structure

The `rich-template.md` defines 8 sections:

| Section | Purpose |
|:--------|:--------|
| 1. Project Overview | Problem/solution description |
| 2. Technical Architecture | Components table + agent design |
| 3. Implementation Details | Step-by-step with code snippets |
| 4. Key Design Principles | Numbered list |
| 5. Errors Encountered & Fixes | Symptom → Root Cause → Fix |
| 6. Configuration Reference | Code patterns |
| 7. Running the Project | Bash entry points |
| 8. Output Architecture | File purpose table |

### Step 4: Progressive Disclosure

> [!TIP]
> Detailed templates are moved to subdirectories to keep `SKILL.md` under 500 lines. This optimizes Claude's context window usage.

**Design Rationale:** A single 1000+ line SKILL.md would consume too much context. Splitting into:
- `SKILL.md` — workflow overview (minimal)
- `assets/rich-template.md` — full template
- `references/priority-guide.md` — reference info

### Step 5: Tool Restrictions

```yaml
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
```

This whitelist approach:
- Prevents accidental destructive operations
- Ensures safe file operations only
- Reduces attack surface

---

## 4. Key Design Principles Learned

1. **Progressive disclosure optimizes context.** Splitting large content into subfiles keeps the main skill file lean while preserving access to full detail.
2. **Tool restrictions are a security feature.** Whitelisting only `Read, Grep, Glob, Bash, Write, Edit` prevents accidental damage from unanticipated tool usage.
3. **Fuzzy matching reduces friction.** Users shouldn't need exact filenames to find their notes.
4. **Rich templates enforce consistency.** The 8-section structure ensures every project gets comprehensive documentation.
5. **References allow on-demand detail.** Priority info stored in `references/` can be loaded when needed without cluttering the main workflow.
6. **Model specification improves consistency.** `model: sonnet` ensures predictable behavior across invocations.

---

## 5. Errors Encountered & Fixes

### Error #1: Skill File Too Large (Context Waste)

**Symptom:**
```
Context window exceeded when loading project-notes skill
```

**Root Cause:**
Original SKILL.md contained all template content, reference docs, and examples — exceeding 500 lines.

**Fix:**
Split into multi-file structure with `assets/` and `references/` subdirectories. SKILL.md now references external files that load on-demand.

---

## 6. Configuration Reference

### Skill Metadata Fields

| Field | Required | Purpose |
|:------|:---------|:--------|
| `name` | Yes | Skill identifier (lowercase, hyphenated) |
| `description` | Yes | Trigger matching — be specific |
| `allowed-tools` | No | Restricts available tools for safety |
| `model` | No | Specifies model for consistent behavior |

### Path Constants

```python
PERSONAL_NOTES_PATH = "/Users/apple/Library/CloudStorage/OneDrive-UniversityofPisa/Startup building/AI Agency Planning/AI Agents Course/personal_notes/"

TEMPLATE_PATH = ".claude/skills/project-notes/assets/rich-template.md"

REFERENCE_PATH = ".claude/skills/project-notes/references/priority-guide.md"
```

### Naming Convention

```
YYYY-MM-DD_Project_Name.md
# Example: 2026-04-26_Project_Notes_Skill.md
```

---

## 7. Running the Project

```bash
# Direct invocation via slash command
/project-notes

# Via terminal
claude --print "/project-notes"

# Natural language trigger
"create notes for MyProject"
```

---

## 8. Output Architecture

| Output | Produced By | Purpose |
| :--- | :--- | :--- |
| **New note file** | Skill (Write tool) | `YYYY-MM-DD_Project_Name.md` in `personal_notes/` |
| **Template expansion** | User input + template | Fills 8-section structure |
| **Search results** | Skill (Grep tool) | Existing note paths |

---

## 9. Related Documentation

| Document | Location | Purpose |
|:---------|:---------|:--------|
| `Skills_Guide.md` | `personal_notes/` | User reference for skills |
| `rich-template.md` | `assets/` | Template for new notes |
| `priority-guide.md` | `references/` | Skill priority reference |

---

## 10. TODO / Next Steps

- [ ] Test fuzzy matching with various project name formats
- [ ] Verify tool restrictions work correctly
- [ ] Add examples to `README.md` showing common workflows
- [ ] Consider adding `Edit` permission for in-place updates