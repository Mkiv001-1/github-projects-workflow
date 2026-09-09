---
name: document-progress
description: Use when you need to document work progress as a comment on a GitHub Issue with a link to a .md results file
triggers:
  - user
  - model
allowed-tools:
  - read
  - exec
  - mcp__github__add_issue_comment
  - mcp__github__get_issue
---

# Document Progress on GitHub Issue

Add a comment to a GitHub Issue documenting what was done, with a link to the results `.md` file.

## Steps

1. Ensure the `.md` results file exists and is committed:
   - Path: `docs/implementation/<task-name>.md` or `docs/research/<task-name>.md`
   - Run `git add <path>` and `git commit` so the file is in the repo.
   - Get the current git SHA: `git rev-parse HEAD`

2. Construct the comment body:

```markdown
## Progress Update — <date>

### What was done
<bullet list of completed work>

### Results
Full details: [docs/implementation/<task-name>.md](link-to-file-on-github)

### Git
- SHA: `<full-sha>`
- Branch: `<branch-name>`

### Artifacts
- <links to any other artifacts: logs, reports, etc.>
```

3. Add the comment to the Issue:
   - `mcp__github__add_issue_comment` with `owner`, `repo`, `issue_number`, `body`.

## Linking to the .md file

The GitHub URL for a file on the default branch:
```
https://github.com/<owner>/<repo>/blob/<branch>/<path-to-file>
```

Use the `blob` URL with the specific commit SHA for a permanent link:
```
https://github.com/<owner>/<repo>/blob/<sha>/<path-to-file>
```

## Fallback: gh CLI

```bash
gh issue comment <num> --repo <owner>/<repo> --body "Progress update..."
```
