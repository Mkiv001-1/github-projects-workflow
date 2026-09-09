---
name: pass-to-skeptic
description: Adversarial review before Done when project policy requires skeptic
triggers:
  - user
  - model
allowed-tools:
  - read
  - exec
  - run_subagent
---

# Pass Task to Skeptic Review

Use when project policy requires skeptic (always, or experiments/research only).

## Steps

1. Set board Status → **In review**.
2. Gather: Issue URL, results `.md` (pushed), git SHA, AGENTS.md rules.
3. Launch skeptic subagent (profile `skeptic` / project `skeptic-review` skill).
4. Skeptic writes verdict `.md` if needed → commit+push → absolute URL comment (`document-progress`).
5. Verdict:
   - **PASS** → Status Done + close Issue
   - **NEEDS REWORK** → Status In Progress
   - **FAIL** → Status Backlog/Ready or new Issue
