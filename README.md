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
| Lifecycle CLI | `scripts/ghp.py` |

## Toolkit — `scripts/ghp.py`

Single Python CLI wrapping `gh`; per-repo config via `ghp.json` or `.devin/ghp.json`
(`{"owner","repo","project"}`), flags, or `GHP_*` env. Statuses set **by name**
(option IDs resolved live — no hardcoding); item-add→list race retried;
epic↔task via `## Sub-tasks` tasklists; `doc` enforces push→verify→comment.

```bash
python scripts/ghp.py board                    # items with Status
python scripts/ghp.py create "Title" --body-file f.md --status Todo --epic 2
python scripts/ghp.py start 12                 # In Progress
python scripts/ghp.py check 12 "pattern"       # tick first unchecked body item
python scripts/ghp.py link 2 12                # epic tasklist
python scripts/ghp.py doc 12 docs/x.md         # verify blob on origin, comment URL
python scripts/ghp.py review 12 / block 12
python scripts/ghp.py done 12 --comment-file evidence.md   # Done + close
python scripts/ghp.py fields                   # dump field/option IDs
```

## Version

0.3.0 — added `scripts/ghp.py` lifecycle CLI (name-resolved statuses, race-safe
item-add, epic tasklists, verified doc comments).
