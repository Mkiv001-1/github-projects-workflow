---
name: create-task
description: Use when you need to create a new GitHub Issue for the current task
triggers:
  - user
  - model
allowed-tools:
  - read
  - exec
  - mcp__github__create_issue
  - mcp__github__list_issues
---

# Create GitHub Issue

Create a GitHub Issue to track the current task.

## Steps

1. Determine the repo: run `git remote -v` to find `owner/repo` from the `origin` remote.

2. Check for an existing open Issue that matches:
   - Use `mcp__github__list_issues` with `state: "open"`.
   - If a matching Issue exists, return its URL and number. Do not create a duplicate.

3. If no match, create a new Issue:
   - `mcp__github__create_issue` with:
     - `owner`: repo owner
     - `repo`: repo name
     - `title`: concise task description (imperative mood, e.g., "Add dark mode toggle")
     - `body`: structured description (see template below)

## Issue Body Template

```markdown
## Task
<one-sentence description>

## Context
<why this task is needed, what triggered it>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] Skeptic review passed

## Artifacts
- Results: <will be linked after completion>
```

## After Creation

1. Record the Issue URL and number.
2. Return them to the caller for use in the workflow lifecycle.

## Fallback: gh CLI

```bash
gh issue create --repo <owner>/<repo> --title "Title" --body "Body"
```
