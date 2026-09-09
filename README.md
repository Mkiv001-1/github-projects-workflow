# github-projects-workflow

Devin CLI plugin that forces every session to track work via GitHub Projects.

## What It Does

- **Mandatory task tracking**: every session creates or identifies a GitHub Issue before starting implementation.
- **Progress documentation**: work is documented as Issue comments with links to `.md` results files.
- **Skeptic review**: completed work is passed to an adversarial reviewer subagent before marking Done.
- **Hard enforcement**: lifecycle hooks block session end if progress is not documented.

## Lifecycle

```
1. CREATE/IDENTIFY → 2. WORK → 3. DOCUMENT → 4. SKEPTIC REVIEW → 5. VERDICT
     ↑                                                        ↓
     └──── NEEDS REWORK / FAIL → fix and re-submit ───────────┘
```

## Installation

```bash
devin plugins install Mkiv001-1/github-projects-workflow
```

## Prerequisites

### GitHub MCP Server

The plugin uses the official GitHub MCP server (remote HTTPS). Set the `GITHUB_MCP_PAT` environment variable to a GitHub Personal Access Token with scopes:
- `repo` (issues, PRs)
- `project` (Projects V2)

```powershell
# Windows (PowerShell)
[System.Environment]::SetEnvironmentVariable("GITHUB_MCP_PAT", "ghp_your_token_here", "User")
```

Alternatively, use `devin mcp login github` for OAuth (requires pre-registered OAuth client).

### Fallback: gh CLI

If the MCP server is unavailable, the plugin falls back to `gh` CLI via `exec`. Ensure `gh` is installed and authenticated:
```bash
gh auth login
```

## Components

| Component | File | Purpose |
|-----------|------|---------|
| Manifest | `.devin-plugin/plugin.json` | Plugin identity |
| MCP config | `.mcp.json` | GitHub MCP server (remote) |
| Always-on rule | `AGENTS.md` | Enforced in every session |
| Hooks | `hooks.json` | Stop + UserPromptSubmit enforcement |
| Main skill | `skills/github-projects-workflow/` | Lifecycle guide |
| Create task | `skills/create-task/` | Create GitHub Issue |
| Document | `skills/document-progress/` | Comment with .md link |
| Skeptic pass | `skills/pass-to-skeptic/` | Launch skeptic subagent |
| Skeptic agent | `agents/skeptic.md` | Adversarial reviewer profile |
| Triggered rule | `rules/task-tracking.md` | Reminder on task start |

## Skills

- `/github-projects-workflow` — main lifecycle (create → work → document → review → verdict)
- `/create-task` — create a GitHub Issue
- `/document-progress` — add a comment with .md link
- `/pass-to-skeptic` — pass to skeptic subagent

## Hooks

- **UserPromptSubmit**: injects a reminder to create/identify an Issue before starting work.
- **Stop**: blocks session end if progress is not documented on the Issue (with skeptic review if task is complete).

## Configuration

The plugin works globally across all projects. Each project's GitHub repo is auto-detected from `git remote -v`.

## License

MIT
