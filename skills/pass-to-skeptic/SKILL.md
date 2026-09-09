---
name: pass-to-skeptic
description: Use when task work is complete and needs adversarial review before marking Done
triggers:
  - user
  - model
allowed-tools:
  - read
  - exec
  - run_subagent
  - mcp__github__add_issue_comment
  - mcp__github__get_issue
---

# Pass Task to Skeptic Review

Launch the skeptic subagent to adversarially review completed work before marking the task Done.

## Steps

1. Gather the context for the skeptic:
   - The GitHub Issue number and URL.
   - The `.md` results file path.
   - The git SHA of the completed work.
   - Any project-specific rules (e.g., AGENTS.md, CLAUDE.md).

2. Launch the skeptic subagent using `run_subagent`:
   - Profile: `skeptic` (custom subagent from this plugin).
   - Task: include the Issue URL, .md file path, git SHA, and what to review.

3. The skeptic will:
   - Read the results file and any referenced artifacts.
   - Check for cherry-picking, post-hoc rationalization, hidden assumptions.
   - Check for completeness and gaps.
   - Check project-specific compliance (e.g., §0 rules if present).
   - Write a verdict comment directly on the GitHub Issue.

4. Read the skeptic's verdict from the subagent output.

5. Based on the verdict:
   - **PASS** → close the Issue, mark as Done.
   - **NEEDS REWORK** → keep Issue open, address specific issues, re-run skeptic.
   - **FAIL** → reopen or create sub-task with fundamental problems.

## Skeptic Task Template

```
Review the completed work for GitHub Issue #<num>: <title>

Issue URL: <url>
Results file: <path-to-md>
Git SHA: <sha>

Review adversarially:
1. Does the result match what was claimed in the Issue?
2. Is there cherry-picking or post-hoc rationalization?
3. Are there hidden assumptions or gaps?
4. Is the work complete per the acceptance criteria?
5. Does it comply with project rules (check AGENTS.md, CLAUDE.md if present)?

Write your verdict as a comment on the Issue using mcp__github__add_issue_comment:
- PASS: work is solid, mark as Done
- NEEDS REWORK: list specific issues to fix
- FAIL: list fundamental problems
```
