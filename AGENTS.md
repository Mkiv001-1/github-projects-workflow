# GitHub Projects Workflow — Mandatory Task Tracking

EVERY session MUST track work via GitHub Projects. No exceptions.

## Lifecycle

1. **CREATE/IDENTIFY** — Find or create a GitHub Issue for the current work before starting implementation.
2. **WORK** — Keep the Issue URL in context. Comment on significant milestones.
3. **DOCUMENT** — Create a `.md` file with results. Add a comment to the Issue linking to it.
4. **SKEPTIC REVIEW** — Pass completed work to the skeptic subagent for adversarial review.
5. **VERDICT** — Update Issue status (Done / Needs rework) based on skeptic verdict.

## Hard Rules

- Do NOT start implementation work without a linked GitHub Issue.
- Do NOT stop the session without documenting progress as an Issue comment.
- Every `.md` results file MUST be linked in an Issue comment.
- Skeptic review is MANDATORY before marking a task Done.
- Issue comments must include: what was done, links to artifacts, git SHA.

## Exemptions

Trivial questions answerable in 1-3 sentences (e.g., "what does this function do?") do NOT require a GitHub Issue. If you are writing code, changing configs, or making multi-step changes — you MUST track via GitHub Projects.

## GitHub MCP Tools

The `github` MCP server provides tools prefixed `mcp__github__`:
- `create_issue` — create a new Issue
- `list_issues` — find existing Issues
- `get_issue` — check Issue state
- `update_issue` — update title/body/state
- `add_issue_comment` — document progress
- `search_issues` — search by keywords

If the MCP server is not available, fall back to `gh` CLI via `exec`:
- `gh issue create --repo <owner>/<repo> --title "..." --body "..."`
- `gh issue comment <num> --repo <owner>/<repo> --body "..."`
- `gh issue list --repo <owner>/<repo> --state open`
- `gh issue view <num> --repo <owner>/<repo>`

## Skills

- `/github-projects-workflow` — main lifecycle skill
- `/create-task` — create a GitHub Issue in the Project
- `/document-progress` — add a comment with .md link to the Issue
- `/pass-to-skeptic` — pass the task to the skeptic subagent
