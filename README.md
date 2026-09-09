# github-projects-workflow

Devin / Cursor plugin: единый GitHub Projects lifecycle для всех репозиториев под `D:\Git`.

## What It Does

- Mandatory Issue + board tracking before implementation
- Board Status as WIP signal (Backlog/Todo → Ready → In Progress → Blocked|In review → Done)
- Progress docs with **absolute** URLs after push+verify
- Body checklist = status; comments = history
- Skeptic review when project policy requires it
- **`gh` CLI is PRIMARY** (MCP optional)

## Lifecycle

```
1. CREATE/IDENTIFY → 2. WORK → 3. DOCUMENT → 4. REVIEW → 5. VERDICT
     ↑                                              ↓
     └──── NEEDS REWORK / FAIL → fix ───────────────┘
```

## Installation (Devin)

```bash
devin plugins install Mkiv001-1/github-projects-workflow
```

## For every D:\Git project

1. Keep this repo as **canon** (`D:\Git\github-projects-workflow`).
2. In each project, add a **thin** local skill with repo/project IDs only:
   - `.devin/skills/github-projects-workflow/` (or `github-project/`)
   - `references/ids.md` — PROJECT_NUM, PROJECT_ID, Status/Priority/Size option IDs
3. Copy or symlink rule: `.devin/rules/task-tracking.md` → point at this lifecycle.
4. Reference from project `AGENTS.md` (do not fork the full lifecycle text).

See `templates/project-local/` for a starter.

## Prerequisites

```powershell
gh auth login
gh auth refresh -s project,read:project
```

MCP github optional; do not depend on it.

## Status semantics

| Status | Meaning |
|--------|---------|
| Backlog / Todo | On board, not ready or not started |
| Ready | Spec clear — can start |
| In Progress | Actively working |
| Blocked | Waiting on operator / external gate |
| In review / Review | Review or skeptic |
| Done | Finished + usually issue closed |

**Ready ≠ Done.**

## Components

| Component | Path |
|-----------|------|
| Canon skill | `skills/github-projects-workflow/SKILL.md` |
| Create task | `skills/create-task/` |
| Document | `skills/document-progress/` |
| Skeptic pass | `skills/pass-to-skeptic/` |
| Rule | `rules/task-tracking.md` |
| Project starter | `templates/project-local/` |

## Version

0.2.0 — hybrid STS+crypto lessons: gh primary, Status roles, absolute URLs, body checklist, PowerShell-safe snippets.
