---
name: create-task
description: Create a GitHub Issue for the current task, add it to the project board, set Ready/Backlog
triggers:
  - user
  - model
allowed-tools:
  - read
  - exec
---

# Create GitHub Issue (+ board)

`gh` CLI only (MCP optional fallback).

## Steps

1. `git remote -v` → `owner/repo`. Load project-local IDs (project number, field IDs).
2. Search duplicates: `gh issue list --repo <owner>/<repo> --state open`.
3. Create if needed:

```powershell
$body = @'
## Task
<one-sentence>

## Context
<why>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>

## Artifacts
- Results: <will be linked after completion>
'@
$body | Set-Content -NoNewline -Encoding utf8 $env:TEMP\issue_body.txt
gh issue create --repo <owner>/<repo> --title "Title" --body-file $env:TEMP\issue_body.txt
Remove-Item $env:TEMP\issue_body.txt
```

4. Add to board:

```powershell
gh project item-add <N> --owner <OWNER> --url <issue-url> --format json
```

5. Set Priority/Size if the project has those fields (`gh project item-edit`).
6. Leave Status at **Backlog** or set **Ready** if acceptance criteria are already clear.
7. Return Issue number + URL. Do not set In Progress until work starts.
