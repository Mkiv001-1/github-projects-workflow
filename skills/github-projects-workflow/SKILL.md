---
name: github-projects-workflow
description: >-
  Canonical GitHub Projects lifecycle for all D:\Git repos. Use when creating,
  searching, updating, or closing tasks; transitioning board Status; documenting
  progress; or auditing project state. gh CLI is PRIMARY.
triggers:
  - user
  - model
allowed-tools:
  - read
  - edit
  - grep
  - glob
  - exec
  - todo_write
  - run_subagent
---

# GitHub Projects Workflow — canonical (D:\Git)

Единый lifecycle для всех репозиториев под `D:\Git`.
Project-local override (IDs, repo, skeptic policy) — в
`.devin/skills/github-projects-workflow/` или `.devin/skills/github-project/`
конкретного репо. **Сначала читай project-local `ids` / identity, потом этот канон.**

## Lessons (обязательны)

1. **`gh` CLI = PRIMARY.** GitHub MCP часто падает — не строить на нём.
2. **Абсолютные blob-URL** в комментариях. Relative `docs/foo.md` = мёртвая ссылка.
3. **Push → verify → comment.** Комментарий со ссылкой до push = 404.
4. **Body checklist = статус; comments = история.** После фазы — обновить `- [ ]` в body.
5. **Issue сразу на board** после create (`gh project item-add`).
6. **Board Status — канонический WIP-сигнал.** Каждая фаза двигает Status.

## Status (семантика)

Рекомендуемые колонки (имена на доске могут отличаться — см. project-local mapping):

| Role | Когда | Типичные имена |
|------|--------|----------------|
| **Backlog** | На доске, спека сырая / не приоритет | Backlog, Todo |
| **Ready** | Критерии ясны, можно брать | Ready |
| **In Progress** | Активная работа | In progress, In Progress |
| **Blocked** | Ждём оператора / внешний гейт | Blocked |
| **In review** | Ревью / skeptic | In review, Review |
| **Done** | Закрыто с доказательством | Done |

**Ready ≠ Done.** Ready = «можно начинать»; Done = «уже закончили» (+ обычно issue closed).

Не выдумывать колонки Design/Plan/Implement — фазы живут в body checklist.
Milestones группируют backlog, это не Status.

**WIP:** ≤2 issues в In Progress (prefer 1). P1/P2 не вытесняют блокирующие P0.

## Repo identity

1. `git remote -v` → `origin` → `owner/repo`
2. Project number, `PROJECT_ID`, field/option IDs — **только из project-local ids**
3. Default branch обычно `main`

## Toolkit — `scripts/ghp.py` (предпочтительный путь)

Один Python CLI вместо ручных gh-заклинаний. Конфиг — `ghp.json` / `.devin/ghp.json`
в репо (`{"owner","repo","project"}`), флаги или `GHP_*` env. Status ставится
**по имени** (option IDs резолвятся живьём), гонка item-add→item-list ретраится,
эпики связываются tasklist'ом `## Sub-tasks`, `doc` гейтит push→verify→comment.

```bash
python <canon>/scripts/ghp.py board | create | status | start | check | link | doc | review | block | done | fields
```

Ручные команды ниже — fallback и для понимания протокола.

## PowerShell (Windows)

Не использовать `gh ... --jq '…|…'` — `|` ломается в PowerShell.
Паттерн:

```powershell
$items = gh project item-list <N> --owner <OWNER> --limit 100 --format json | ConvertFrom-Json
$itemId = ($items.items | Where-Object { $_.content.number -eq <NUM> }).id
```

Issue body / comments — here-string + temp file:

```powershell
$body = @'
## Task
...
'@
$body | Set-Content -NoNewline -Encoding utf8 $env:TEMP\issue_body.txt
gh issue create --repo <owner>/<repo> --title "Title" --body-file $env:TEMP\issue_body.txt
Remove-Item $env:TEMP\issue_body.txt
```

## Phase 1: CREATE / IDENTIFY

1. Search open issues (`gh issue list --repo … --state open`).
2. Match exists → use it. Else create (body template ниже).
3. `gh project item-add <N> --owner <OWNER> --url <issue-url>`
4. Verify item on board; set Priority/Size if project has those fields.
5. Status = **Backlog** или **Ready** (если спека уже полная). Не In Progress, пока работа не началась.

**HARD GATE:** без Issue **и** board item — не начинать реализацию.

### Issue body template

```markdown
## Task
<one sentence>

## Context
<why>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>

## Artifacts
- Results: <link after completion>
```

(Проекты с обязательным skeptic добавляют `- [ ] Skeptic review passed`.)

## Phase 2: WORK

0. Status → **In Progress**. Если ждём оператора → **Blocked** и стоп.
1. Держать Issue URL в контексте.
2. Значимые вехи → comment (кратко).
3. После каждой lifecycle-фазы → **обновить body checklist** (`gh issue edit --body-file`).

## Phase 3: DOCUMENT

1. Записать `.md` (путь — по соглашению проекта: `docs/implementation/`, `docs/decisions/`, …).
2. **Commit + push** на remote default branch.
3. Verify:

```powershell
gh api repos/<owner>/<repo>/contents/<path> --jq ".html_url"
```

4. Comment с **абсолютным** URL:

```
https://github.com/<owner>/<repo>/blob/main/<path>
```

(или `/blob/<sha>/…` для permanent link).

5. Verify comment: `gh issue view <num> --comments`
6. Обновить body checklist.

## Phase 4: REVIEW / SKEPTIC

0. Status → **In review** (Review).
1. Skeptic: **обязателен**, если project-local policy так говорит, или задача — experiment/research.
   Иначе — self-review / human review по AGENTS.md проекта.
2. Вердикт → comment (+ `.md` если есть), checklist обновить.

## Phase 5: VERDICT / CLOSE

| Outcome | Status | Issue |
|---------|--------|-------|
| PASS | **Done** | close + evidence comment |
| NEEDS REWORK | **In Progress** | keep open |
| FAIL / split | **Backlog** / **Ready** | reopen or new issue |
| Waiting | **Blocked** | comment with reason |

Перед close: body checklist полностью отмечен; Status=Done **и** issue closed вместе.

## Set Status (snippet)

```powershell
gh project item-edit --id $itemId --project-id $PROJECT_ID `
  --field-id $STATUS_FIELD_ID --single-select-option-id $OPTION_ID
```

Option IDs — только из project-local ids file.

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| MCP github failed | Use `gh` — primary |
| Relative path in comment | Absolute blob URL |
| Comment before push | Push + verify contents API, then comment |
| Comments only, body stale | Update body checklist each phase |
| Issue not on board | `item-add` immediately after create |
| Status stuck on Backlog/Todo while working | Set In Progress at Phase 2 |
| Invented Status columns | Checklist + milestones instead |
| `git add -A` | Explicit file list |
| bash heredoc in PowerShell | `@'…'@` here-string |

## Exemption

Trivial Q&A (1–3 sentences, no code/config changes) — без Issue.
