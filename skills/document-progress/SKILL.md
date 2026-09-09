---
name: document-progress
description: Document progress on a GitHub Issue with a verified absolute link to a pushed .md file
triggers:
  - user
  - model
allowed-tools:
  - read
  - exec
---

# Document Progress

## Steps

1. Ensure the `.md` file exists, is committed, and **pushed** to the remote default branch.
2. Verify the file is on the remote:

```powershell
gh api repos/<owner>/<repo>/contents/<path> --jq ".html_url"
```

If this errors — push first. Do not comment yet.

3. Comment with absolute URL:

```powershell
$msg = @'
## Progress Update — <date>

### What was done
- …

### Results
https://github.com/<owner>/<repo>/blob/main/<path>

### Git
- SHA: `<full-sha>`
- Branch: `main`
'@
gh issue comment <num> --repo <owner>/<repo> --body $msg
```

4. Verify: `gh issue view <num> --repo <owner>/<repo> --comments`
5. Update the Issue body checklist to match reality.
