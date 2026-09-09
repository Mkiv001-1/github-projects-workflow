# GitHub Projects Workflow — Mandatory Task Tracking

EVERY non-trivial session MUST track work via GitHub Projects.

**Canon:** `skills/github-projects-workflow/SKILL.md`  
**Tooling:** `gh` CLI is PRIMARY. MCP github is optional fallback only.

## Lifecycle

1. **CREATE/IDENTIFY** — Issue + board item before implementation.
2. **WORK** — Status = In Progress (or Blocked). Update body checklist.
3. **DOCUMENT** — Push `.md` first, then absolute URL in comment.
4. **REVIEW** — Skeptic / self-review per project policy. Status = In review.
5. **VERDICT** — Status = Done + close Issue with evidence.

## Hard Rules

- No implementation without linked Issue **and** project board item.
- Board Status is the WIP signal; keep ≤2 In Progress.
- Ready = can start; Done = finished (not the same).
- Absolute blob URLs only; verify remote file before commenting.
- Body checklist is status; comments are history.
- No `git add -A` / `git add .`.

## Exemptions

Trivial Q&A (1–3 sentences, no code/config changes).

## Skills

- `/github-projects-workflow` — main lifecycle
- `/create-task` — create Issue + board
- `/document-progress` — verified comment with .md link
- `/pass-to-skeptic` — adversarial review (when required)
