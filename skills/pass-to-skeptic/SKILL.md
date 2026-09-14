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

1. **Round control:** `python <canon>/scripts/ghp.py rounds <issue>` —
   counts prior Skeptic Review verdicts. If NEEDS REWORK >= cap (3,
   same limit as the self-heal cap): `--escalate` posts a comment and
   sets Status → **Blocked**. Do NOT launch another silent rework cycle —
   a human decides whether the approach itself is wrong.
2. Set board Status → **In review**.
3. Gather: Issue URL, results `.md` (pushed), git SHA, AGENTS.md rules,
   and — if the repo has `docs/failures/INDEX.md` — the failure classes
   matching the diff (`python docs/failures/check.py --diff`).
4. Launch skeptic subagent (profile `skeptic` / project `skeptic-review`
   skill). The prompt MUST include the touched file list, the round
   number from step 1, and instruct the skeptic to check
   `docs/failures/INDEX.md` for known classes in that area
   (cite F-NNN, don't re-derive).
5. Skeptic writes verdict `.md` if needed → commit+push → absolute URL comment (`document-progress`).
6. Verdict:
   - **PASS** → Status Done + close Issue
   - **NEEDS REWORK** → Status In Progress. Each finding maps to a journal
     class (bump `instances`/`last seen` or write a new entry in the same
     commit as the rework). The rework commit MUST re-run the probes that
     caught the findings AND the suite covering the touched area — not
     only the new fix.
   - **FAIL** → Status Backlog/Ready or new Issue
