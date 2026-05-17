# Memory System & Workspace Setup
**Date:** 2026-04-26

## 1. Project Overview

Established a shared User Memory system for parallel terminal sessions in the AI Agency Planning workspace. Refactored the `/project-notes` skill into a multi-file architecture using Progressive Disclosure. Enforced mandatory documentation rules across all AI Agents Course projects. The workspace is now self-documenting — Claude auto-records progress after every implementation milestone.

**Core Purpose:** Enable all Claude Code terminals working in this directory tree to share context, maintain consistent documentation, and hand off work seamlessly between sessions without losing state.

---

## 2. The Problem This Solves

When working across multiple Claude Code terminals simultaneously:
- Terminal 1 might be modifying the Followup Agent
- Terminal 2 might be working on n8n workflows
- Terminal 3 might be reviewing local AI/ComfyUI setup

**Without shared memory:**
- Each terminal only knows what happened in its own conversation
- Work done in Terminal 1 is invisible to Terminal 2
- Massive duplication of effort, context loss, inconsistent approaches

**With shared memory:**
- All terminals read from the same memory files
- Changes made in one terminal are immediately visible to others
- Session handoffs preserve continuity

---

## 3. Memory System Architecture

### Memory Directory Location
```
~/.claude/projects/-Users-apple-Library-CloudStorage-OneDrive-UniversityofPisa-Startup-building-AI-Agency-Planning/memory/
```

### The Four Core Memory Files

| File | Type | Purpose |
|:-----|:-----|:--------|
| **MEMORY.md** | index | Master index pointing to all memory files |
| **project_context.md** | project | High-level AI agency startup goals, current focus, ongoing initiatives |
| **user_profile.md** | user | User identity, tech stack, design standards, workflow rules, multi-session sync |
| **session_summary.md** | reference | Continuous session log tracking last completed task, blockers, next steps |

### How Memory Loads

Claude Code auto-loads `MEMORY.md` (the short index, ~5 lines) at session start. Referenced files like `user_profile.md` and `project_context.md` are **lazy-loaded on demand** — Claude only reads them when the conversation actually needs them, keeping context efficient.

### Memory File Format

All memory files use frontmatter for metadata:
```markdown
---
name: filename
description: One-line description for relevance matching
type: user|project|reference|feedback
originSessionId: (optional) session that created this
---

[Content]
```

### Memory Type Guidelines

| Type | When to Use | Example |
|:-----|:------------|:--------|
| **user** | User preferences, identity, tech stack | user_profile.md |
| **project** | Project goals, ongoing work, high-level context | project_context.md |
| **reference** | External system pointers, session logs | session_summary.md |
| **feedback** | Rules from user corrections/confirmations | feedback_testing.md |

---

## 4. Skill Refactoring: Progressive Disclosure

### The Problem with Large Skills

Original `/project-notes` skill contained:
- Full workflow documentation
- Complete template content
- All reference materials
- Examples and edge cases

**Result:** SKILL.md exceeded 500 lines, consuming excessive context window.

### The Solution: Multi-File Architecture

```
project-notes/
├── SKILL.md                    # Main entry point (workflow overview only)
├── README.md                   # Skill documentation
├── assets/
│   └── rich-template.md        # Full 8-section template
└── references/
    └── priority-guide.md        # Detailed reference materials
```

### Progressive Disclosure in Practice

**SKILL.md** — Lean main file (~180 lines)
- Contains workflow overview
- References external files for detail
- Stays within context budget

**assets/rich-template.md** — Full template (~96 lines)
- Loaded when creating new notes
- Contains all 8 sections with prompts

**references/priority-guide.md** — Reference materials (~290 lines)
- Loaded on-demand for detailed guidance
- Contains skill precedence rules

### Skill Refinement (Post-Setup)

After the initial refactor, two enhancements were added:

1. **Detail Standard (150+ line minimum)**: New project notes must be comprehensive — modeled after reference implementation guides (`10_Coder_Me_Implementation.md`, `07_Stock_Picker_Implementation.md`) with architecture details, code snippets, troubleshooting, and design principles.
2. **Reference Directory Instruction**: Infrastructure/meta-project notes (memory system, skill architecture) must use the `references/` directory guides for structural examples.

### Tool Restrictions

```yaml
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
```

Whitelist approach prevents accidental destructive operations while allowing safe file operations.

---

## 5. Rule Enforcement: Workflow & Documentation Rules

### Mandatory Rules for AI Agents Course/projects/

Per `CLAUDE.md` requirements:

1. **Post-Implementation Documentation**
   - After any code creation/modification/debugging in `AI Agents Course/projects/`
   - Run `/project-notes [Project Name]` to update implementation notes
   - This ensures detailed tracking per specific project

2. **Memory System Sync**
   - After completing milestones or major workflow changes
   - Update `session_summary.md` with progress
   - This enables session handoffs across terminals

3. **Session Handoff on Memory Sync**
   - After every significant task, update `session_summary.md` (Last Completed, Blockers, Next Steps)
   - Also append a dated entry to `conversation_summaries.md` with the conversation content
   - This enables full handoff between parallel terminals

4. **Context Awareness**
   - When working in this directory, Claude reads `MEMORY.md` for shared context
   - Considers `project_context.md` for high-level alignment
   - Uses `session_summary.md` for continuity

### Why These Rules Matter

- **Multi-terminal workflow** — Same context available to all terminals
- **No context loss** — Session handoffs preserve continuity
- **Consistent documentation** — Every project gets detailed notes
- **Self-documenting workspace** — Claude auto-records, user doesn't have to remember

---

## 6. Running the Projects

### Memory System
```bash
# Memory files are auto-loaded by Claude Code
# No manual commands needed — Claude reads MEMORY.md automatically
```

### Project Notes
```bash
# After code changes in AI Agents Course/projects/
/project-notes [Project Name]

# Example:
/project-notes Followup Agent
/project-notes Deep Research
/project-notes Email CRM Agent
```

### Session Summary Updates
```bash
# Manual updates can be done by asking Claude:
"Update my session summary with [what you just did]"
```

---

## 7. Key Design Principles

1. **Shared context across terminals** — All Claude Code instances read from the same memory files
2. **Progressive disclosure** — Large content split into subfiles, loaded on-demand
3. **Tool restrictions** — Whitelist approach for safety
4. **Self-documenting workspace** — Claude auto-records, no manual effort required
5. **Session handoffs** — `session_summary.md` enables continuity between terminals
6. **Layered memory** — project_context (high-level) → session_summary (continuity) → project notes (detailed)

---

## 8. Output Architecture

| Output | Produced By | Purpose |
|:-------|:------------|:--------|
| **Memory files** | System/Creator | Shared context across terminals |
| **Project notes** | `/project-notes` skill | Detailed implementation tracking per project |
| **Session log** | Claude after milestones | Continuity for session handoffs |
| **Documentation** | Auto-generated | Record of achievements and setup |

---

## 9. Troubleshooting

### Memory Not Loading?
- Check that `MEMORY.md` exists at the memory directory path
- Verify all linked files exist
- Claude Code loads MEMORY.md at startup — restart may be needed

### Terminal Not Seeing Updates?
- Memory files are file-based — changes are immediate
- No sync command needed
- New messages in terminal will read updated files

### Project Notes Not Finding Files?
- Check that you're in `AI Agents Course/projects/` subdirectory
- Ensure `personal_notes/` exists in `AI Agents Course/`
- Use exact project name as it appears in directory

---

## 10. Conversation Logging System

A dual-layer system for capturing conversation history across all parallel terminals.

### Layer 1: SQLite Timeline DB (Auto-Hooks)
- **File**: `conversations.db` in the memory directory
- **WAL Mode**: Enabled for safe concurrent reads/writes from parallel terminals
- **Schema**: `sessions` (id, started_at, ended_at, summary) + `messages` (id, session_id, role, content, timestamp)
- **Hooks**: `UserPromptSubmit` + `Stop` events in `.claude/settings.local.json` auto-log every turn
- **Limitation**: Hooks only pass session_id/metadata, not full message text

### Layer 2: Conversation Summaries (Manual)
- **File**: `conversation_summaries.md` in the memory directory
- **Trigger**: Appended every time `session_summary.md` is updated (end of significant task)
- **Content**: Claude-written summary of the conversation's key points

### CLI Viewer
- **Script**: `check_conversations.sh` (in memory directory)
- **Usage**: `bash check_conversations.sh --last 5` — any terminal can query the log

## 11. Related Documentation

| Document | Location | Purpose |
|:---------|:---------|:--------|
| `Skills_Guide.md` | `personal_notes/` | User reference for all skills |
| `05_Followup_Agent_Implementation.md` | `personal_notes/` | Example of detailed project notes |
| `CLAUDE.md` | Project root | Project-level rules and requirements |
| `MEMORY.md` | Memory dir | Master index for memory system |
| `user_profile.md` | Memory dir | User identity, tech stack, standards, workflow rules |
| `session_summary.md` | Memory dir | Live handoff log for parallel terminals |
| `conversation_summaries.md` | Memory dir | Running content summaries appended on each memory sync |
| `conversations.db` | Memory dir | SQLite timeline DB with auto-hooks (UserPromptSubmit + Stop) |
| `check_conversations.sh` | Memory dir | CLI viewer for conversation DB |
| `log_conversation.sh` | Memory dir | Hook script for auto-logging |
| `SKILL.md` | `.claude/skills/project-notes/` | Project notes skill (includes Detail Standard: 150+ line minimum) |
