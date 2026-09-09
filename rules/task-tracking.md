---
description: Triggers when starting work on a task — reminds to create or identify a GitHub Issue before implementation
globs: ["*"]
---

# Task Tracking Reminder

Before starting any implementation work (writing code, changing configs, multi-step changes):

1. Check if you have a GitHub Issue for this task.
2. If not, use `/create-task` to create one.
3. If yes, keep the Issue URL in context.

**Do not start implementation without a linked GitHub Issue.**

This rule is enforced by the `github-projects-workflow` plugin. The Stop hook will block session end if progress is not documented on the Issue.

## Exemption

Trivial questions (1-3 sentence answers, no code changes) are exempt from Issue tracking.
