# Parallel AI Coding: Using Git Worktrees with Claude Code

This guide explains how to run multiple **Claude Code** sessions in parallel using `git worktree`. This allows you to have multiple AI agents working on different features of the same project simultaneously without them clashing.

---

## 1. Do I need to Push to GitHub?
**NO.** 
Git Worktrees are a **purely local** feature. They happen entirely on your Mac's hard drive.
- You do NOT need to push to a server.
- You do NOT even need a remote repository (like GitHub).
- You only need to have Git initialized locally on your folder.

---

## 2. The Step-by-Step Plan (Start to Finish)

### Phase A: Setup (One-time only)
If your project folder isn't already a Git repository, run these commands:
```bash
# Initialize git
git init

# Add and commit your current files (so git knows they exist)
git add .
git commit -m "Initial commit of lead generation project"
```

### Phase B: Launching a Parallel Session
Let's say you are working on your main branch, but you want a second Claude to start working on a "Web Research" feature in the background.

1. **Create the Worktree:**
   Run this in your main folder:
   ```bash
   git worktree add ../research-session -b research-feature
   ```
   *This creates a new folder called `research-session` one level up, and switches it to a new branch called `research-feature`.*

2. **Run Claude in Folder 1 (Main):**
   ```bash
   cd ~/your-project
   claude
   # Tell it: "Improve the lead extraction logic"
   ```

3. **Run Claude in Folder 2 (Parallel):**
   Open a **new Terminal Tab** and run:
   ```bash
   cd ~/research-session
   claude
   # Tell it: "Build the new Web Research tool"
   ```

### Phase C: Bringing the Work Together
Once the parallel Claude is finished:
1. Go back to your **Main Folder**.
2. Merge the work:
   ```bash
   git merge research-feature
   ```
3. Delete the worktree folder when done:
   ```bash
   git worktree remove ../research-session
   ```

---

## 3. Critical Rules for Success
1. **Unique Files:** Try to give each Claude different files to work on. If both Claudes try to edit `lead_gen_crew.py` at the same exact second, you will have a "Merge Conflict" that you'll have to fix later.
2. **Commit Often:** Tell your Claudes to `/git commit` their work frequently. This makes merging back to your main branch much smoother.
3. **Path Awareness:** Remember that because they are in different folders, relative paths (like `../data`) might behave differently. Always use absolute paths or stay within the project root.

---

## 4. Why this is the "Ultimate" AI Workflow
Instead of sitting and watching a progress bar for 10 minutes while Claude scrapes leads, you can be actively coding a UI, writing docs, or building a new tool in a parallel window. It effectively doubles or triples your productivity.
