---
description: Hard gate — no implementation without GitHub Issue + project board item. Canonical for all D:\Git projects.
globs: ["*"]
---

# Task Tracking

Before any implementation (code, configs, multi-step changes):

1. Identify or create a GitHub Issue (`gh issue list` / `gh issue create`).
2. Ensure the Issue is on the project's GitHub Project board (`gh project item-add`).
3. When work starts — set board Status to **In Progress** (or **Blocked** if waiting).

**Do not start implementation without a linked Issue and board entry.**

Canonical lifecycle: `skills/github-projects-workflow/SKILL.md` in this plugin,
plus project-local IDs under the repo's `.devin/skills/`.

## When work completes

1. Write results `.md` if the project expects it.
2. Commit + **push**, verify via `gh api repos/…/contents/…`.
3. Comment with **absolute** GitHub blob URL.
4. Update Issue body checklist.
5. Set Status → Done and close the Issue (after review/skeptic per project policy).

## Exemption

Trivial questions (1–3 sentence answers, no code changes) are exempt.
