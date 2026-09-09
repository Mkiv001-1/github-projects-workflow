---
name: github-projects-workflow
description: Use when starting any task or session — enforces GitHub Projects lifecycle (create task, work, document, skeptic review, verdict)
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - glob
  - exec
  - todo_write
  - run_subagent
  - mcp__github__create_issue
  - mcp__github__list_issues
  - mcp__github__update_issue
  - mcp__github__add_issue_comment
  - mcp__github__get_issue
  - mcp__github__search_issues
---

# GitHub Projects Workflow — Session Lifecycle

Every session follows this lifecycle. No skipping phases.

## Phase 1: CREATE/IDENTIFY Task

Before starting any implementation work:

1. Determine the current repo: run `git remote -v` to find `owner/repo`.
2. Search for an existing open Issue that matches the current task:
   - Use `mcp__github__list_issues` with `state: "open"` for the repo.
   - Or use `mcp__github__search_issues` with keywords from the user's request.
3. If a matching Issue exists — use it. Record the Issue URL and number.
4. If no matching Issue — create one:
   - Use `/create-task` skill, or `mcp__github__create_issue` directly.
   - Title: concise description of the task.
   - Body: hypothesis/requirements, acceptance criteria, context.
5. Record the Issue URL in your todo list as the first item.

**HARD GATE**: Do not proceed to Phase 2 without a linked Issue.

## Phase 2: WORK

1. Keep the Issue URL in context throughout the session.
2. When you hit a significant milestone (test passes, feature works, bug fixed):
   - Add a comment to the Issue with a brief update.
3. If the task scope changes — update the Issue body via `mcp__github__update_issue`.

## Phase 3: DOCUMENT

When the work is complete (or at a natural checkpoint):

1. Create a `.md` file with results:
   - Path: `docs/implementation/<task-name>.md` or `docs/research/<task-name>.md`
   - Content: what was done, how, results, git SHA, links to artifacts.
2. Add a comment to the Issue:
   - Use `/document-progress` skill or `mcp__github__add_issue_comment` directly.
   - Comment must include: summary of work, link to the `.md` file, git SHA.
3. Commit and push the `.md` file so the link is resolvable.

## Phase 4: SKEPTIC REVIEW

Before marking the task Done:

1. Use `/pass-to-skeptic` skill to launch the skeptic subagent.
2. The skeptic reviews the work adversarially:
   - Does the result match what was claimed?
   - Is there cherry-picking or post-hoc rationalization?
   - Are there hidden assumptions or gaps?
   - Is the work complete?
3. The skeptic writes its verdict as a comment on the Issue.

## Phase 5: VERDICT

Based on the skeptic's verdict:

| Skeptic verdict | Action |
|----------------|--------|
| PASS | Update Issue to closed, mark as Done in Project |
| NEEDS REWORK | Keep Issue open, add specific issues to fix, continue working |
| FAIL | Reopen or create sub-task with fundamental problems listed |

Update Issue state via `mcp__github__update_issue` (state: "closed" for PASS).

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll create the Issue after I finish" | No. Create BEFORE starting. Preregistration matters. |
| "This is too small for an Issue" | If you're writing code or changing configs, it needs an Issue. |
| "I'll document later" | Document at checkpoints, not at the end. Memory is lossy. |
| "Skeptic review is overkill" | Skeptic catches cherry-picking and gaps. Always run it. |
| "The user didn't ask for tracking" | This plugin enforces it regardless. The workflow is mandatory. |

## Fallback: gh CLI

If the GitHub MCP server is unavailable, use `gh` CLI via `exec`:

```bash
# Create issue
gh issue create --repo <owner>/<repo> --title "Title" --body "Body"

# List open issues
gh issue list --repo <owner>/<repo> --state open

# Add comment
gh issue comment <num> --repo <owner>/<repo> --body "Progress update..."

# Close issue
gh issue close <num> --repo <owner>/<repo>
```
