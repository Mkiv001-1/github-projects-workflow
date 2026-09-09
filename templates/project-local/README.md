# Project-local adapter (copy into each repo)

```
.devin/
  rules/task-tracking.md          # hard gate (can be short; points to canon)
  skills/github-projects-workflow/
    SKILL.md                      # identity + policy + link to canon
    references/ids.md             # PROJECT_NUM, IDs, status name mapping
```

## SKILL.md skeleton

```markdown
---
name: github-projects-workflow
description: Project-local GitHub Projects adapter for <REPO>. Canon: D:\Git\github-projects-workflow
---

# <REPO> — GitHub Projects

**Canon:** `D:\Git\github-projects-workflow\skills\github-projects-workflow\SKILL.md`
Read canon first; below is identity + policy only.

## Identity

- Owner/repo: `OWNER/REPO`
- Project: #<N> `Name` — https://github.com/users/OWNER/projects/N
- Default branch: `main`
- IDs: `references/ids.md`

## Status name mapping

| Role (canon) | Local name | Option ID |
|--------------|------------|-----------|
| Backlog | … | … |
| Ready | … | … |
| In Progress | … | … |
| Blocked | … | … |
| In review | … | … |
| Done | … | … |

## Policy

- Skeptic: always | experiments-only | never
- Results path: `docs/…`
- WIP limit: 2
- Priority/Size fields: yes/no
```

## ids.md skeleton

```markdown
REPO = OWNER/REPO
PROJECT_NUM = N
OWNER = OWNER
PROJECT_ID = PVT_…
STATUS_FIELD_ID = PVTSSF_…
# option ids…
```

After creating a new GitHub Project, fill IDs via:

```powershell
gh project field-list <N> --owner <OWNER>
```
