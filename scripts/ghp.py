#!/usr/bin/env python3
"""ghp — GitHub Projects lifecycle CLI for all C:\\git repos.

Wraps `gh` CLI. Fixes the manual-workflow pitfalls:
  * status set by NAME (option IDs resolved dynamically per project)
  * item-add -> item-list race handled with retry
  * epic <-> task linkage via "## Sub-tasks" tasklist in epic body
  * push -> verify -> comment enforced for doc comments

Config resolution (first hit wins):
  --repo/--project/--owner flags > ./ghp.json | ./.devin/ghp.json > env
Config file keys: {"owner": "...", "repo": "owner/name", "project": 5}

Subcommands:
  create TITLE [--body-file F] [--status NAME] [--epic N]
  board [--status NAME]           list items: num, status, title
  status NUM NAME                 set board Status by name
  start NUM | review NUM | block NUM | done NUM [--comment-file F]
  check NUM PATTERN               tick first unchecked "- [ ]" line matching
  link EPIC TASK                  append "- [ ] #TASK" under ## Sub-tasks
  comment NUM --file F            add comment
  doc NUM PATH [--text S]         verify blob on origin/main, comment URL
  rounds NUM [--cap N] [--escalate]
                                  count Skeptic Review verdicts on NUM;
                                  exit 2 when NEEDS REWORK >= cap (def 6)
  fields                          dump project fields + option ids
"""

import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

STATUS_FIELD_NAME = "status"
STATUS_ALIASES = {
    "in progress": "in progress", "inprogress": "in progress", "wip": "in progress",
    "review": "review", "in review": "review", "blocked": "blocked",
    "todo": "todo", "backlog": "todo", "ready": "ready", "done": "done",
}


def die(msg, code=1):
    print(f"ghp: error: {msg}", file=sys.stderr)
    sys.exit(code)


def gh(*args, check=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        die(f"gh {' '.join(args)} -> {r.returncode}\n{r.stderr.strip()}")
    return r


def load_config(args):
    cfg = {}
    for p in ("ghp.json", os.path.join(".devin", "ghp.json")):
        if os.path.isfile(p):
            cfg = json.load(open(p, encoding="utf-8"))
            break
    owner = args.owner or cfg.get("owner") or os.environ.get("GHP_OWNER")
    repo = args.repo or cfg.get("repo") or os.environ.get("GHP_REPO")
    project = args.project or cfg.get("project") or os.environ.get("GHP_PROJECT")
    if not (owner and repo and project):
        die("need owner/repo/project: flags, ghp.json (.devin/), or GHP_* env")
    return owner, repo, int(project)


def project_id(owner, num):
    r = gh("project", "view", str(num), "--owner", owner, "--format", "json")
    return json.loads(r.stdout)["id"]


def project_items(owner, num):
    r = gh("project", "item-list", str(num), "--owner", owner,
           "--format", "json", "--limit", "200")
    return json.loads(r.stdout)["items"]


def find_item(owner, num, issue_num, retries=6):
    for i in range(retries):
        for it in project_items(owner, num):
            if it["content"].get("number") == issue_num:
                return it
        if i < retries - 1:
            time.sleep(1.5)
    die(f"issue #{issue_num} not on project {num} after {retries} tries")


def status_options(owner, proj_id):
    """-> {normalized_option_name: option_id} for the Status field."""
    q = """query($id:ID!){node(id:$id){... on ProjectV2{
      fields(first:30){nodes{... on ProjectV2SingleSelectField{
        id name options{id name}}}}}}}"""
    r = gh("api", "graphql", "-f", f"query={q}", "-F", f"id={proj_id}")
    fields = r.stdout and json.loads(r.stdout)["data"]["node"]["fields"]["nodes"]
    for f in fields:
        if f.get("name", "").lower() == STATUS_FIELD_NAME:
            return {o["name"].strip().lower(): o["id"] for o in f["options"]}, f["id"]
    die(f"no '{STATUS_FIELD_NAME}' single-select field on project")


def set_status(owner, proj_num, proj_id, issue_num, status_name):
    opts, field_id = status_options(owner, proj_id)
    want = STATUS_ALIASES.get(status_name.strip().lower(), status_name.strip().lower())
    # exact match first, then prefix match ("in" -> "in progress")
    opt_id = opts.get(want)
    if not opt_id:
        hits = [k for k in opts if k.startswith(want) or want in k]
        if len(hits) == 1:
            opt_id = opts[hits[0]]
    if not opt_id:
        die(f"status '{status_name}' not found; options: {', '.join(opts)}")
    item = find_item(owner, proj_num, issue_num)
    gh("project", "item-edit", "--project-id", proj_id, "--id", item["id"],
       "--field-id", field_id, "--single-select-option-id", opt_id)
    print(f"#{issue_num} status -> {status_name}")


def issue_body(repo, num):
    r = gh("issue", "view", str(num), "--repo", repo, "--json", "body", "-q", ".body")
    return r.stdout


def edit_body(repo, num, body):
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".md", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(body)
    try:
        gh("issue", "edit", str(num), "--repo", repo, "--body-file", path)
    finally:
        os.unlink(path)


def cmd_create(owner, repo, proj_num, proj_id, a):
    args = ["issue", "create", "--repo", repo, "--title", a.title]
    if a.body_file:
        args += ["--body-file", a.body_file]
    elif a.body:
        args += ["--body", a.body]
    else:
        args += ["--body", ""]
    url = gh(*args).stdout.strip()
    num = int(url.rstrip("/").rsplit("/", 1)[1])
    gh("project", "item-add", str(proj_num), "--owner", owner, "--url", url)
    if a.status:
        set_status(owner, proj_num, proj_id, num, a.status)
    if a.epic:
        cmd_link(repo, a.epic, num)
    print(url)


def cmd_link(repo, epic, task):
    body = issue_body(repo, epic)
    marker = "## Sub-tasks"
    line = f"- [ ] #{task}"
    if line in body:
        print(f"#{task} already linked in #{epic}")
        return
    if marker not in body:
        body += f"\n\n{marker}\n{line}\n"
    else:
        body = body.replace(marker, marker + "\n" + line, 1)
    edit_body(repo, epic, body)
    print(f"linked #{task} -> epic #{epic}")


def cmd_check(repo, num, pattern):
    body = issue_body(repo, num)
    lines, hit = body.splitlines(), False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("- [ ]") and pattern.lower() in ln.lower():
            lines[i] = ln.replace("- [ ]", "- [x]", 1)
            hit = True
            break
    if not hit:
        die(f"no unchecked item matching '{pattern}' in #{num}")
    edit_body(repo, num, "\n".join(lines) + "\n")
    print(f"#{num}: checked '{pattern}'")


def cmd_board(owner, proj_num, only=None):
    items = project_items(owner, proj_num)
    for it in sorted(items, key=lambda x: x["content"].get("number", 0)):
        st = it.get("status") or "-"
        if only and st.lower() != only.lower():
            continue
        c = it["content"]
        print(f"#{c.get('number','?'):<4} {st:<12} {c.get('title','')[:75]}")


def cmd_doc(owner, repo, num, path, text):
    r = gh("api", f"repos/{repo}/contents/{path}", "-q", ".html_url", check=False)
    if r.returncode != 0 or "blob" not in r.stdout:
        die(f"{path} not found on origin — push first (push -> verify -> comment)")
    url = r.stdout.strip()
    body = f"{text or 'Docs'}: {url}"
    gh("issue", "comment", str(num), "--repo", repo, "--body", body)
    print(f"#{num} <- {url}")


def cmd_done(owner, repo, proj_num, proj_id, num, comment_file):
    if comment_file:
        gh("issue", "comment", str(num), "--repo", repo, "--body-file", comment_file)
    set_status(owner, proj_num, proj_id, num, "Done")
    gh("issue", "close", str(num), "--repo", repo)
    print(f"#{num} Done + closed")


# A skeptic round leaves evidence in issue comments in two formats:
#   heading:  "## Skeptic Review [rN] — VERDICT"  (authoritative)
#   echo:     "Skeptic rN VERDICT ..."            (implementor summaries)
# Both are line-anchored — mid-prose mentions ("the skeptic review -
# pass criteria") don't count. Round identity = its rN slot (F-011:
# dedupe identity); a heading without rN starts a NEW round — comments
# are processed chronologically and a verdict heading always precedes
# its own round's echoes. Echoes never overwrite a heading-sourced slot.
HEAD_RE = re.compile(
    r"^\s*#{1,6}\s+skeptic\s+review\s*(?:r(\d+))?\s*[—–-]+\s*"
    r"(PASS|NEEDS\s+REWORK|FAIL)\b",
    re.I | re.M)
SUMM_RE = re.compile(
    r"^\s*skeptic\s+r(\d+)\s*[—–-]?\s*(PASS|NEEDS\s+REWORK|FAIL)\b",
    re.I | re.M)


def _norm_verdict(v):
    return " ".join(v.split()).upper()


FENCE_RE = re.compile(r"```.*?```", re.S)


def count_rounds(comments):
    """comments = [body, ...] in chronological order ->
    (slots {round_no: verdict}, heading_sourced {round_no}).

    Matches within a comment are processed in TEXTUAL order — a verdict
    heading following a `Skeptic rN` recap claims the NEXT slot, it does
    not steal the recapped round's slot. Heading verdicts are
    authoritative over echoes for the same slot; echoes fill gaps only.
    Fenced code blocks are stripped — a quoted verdict template is not a
    verdict."""
    slots, heading_slots = {}, set()
    for body in comments:
        body = FENCE_RE.sub("", body)
        matches = ([(m.start(), m, True) for m in HEAD_RE.finditer(body)]
                   + [(m.start(), m, False) for m in SUMM_RE.finditer(body)])
        for _, m, is_head in sorted(matches, key=lambda t: t[0]):
            v = _norm_verdict(m.group(2))
            n = int(m.group(1)) if m.group(1) else None
            if is_head:
                if n is None:
                    n = (max(slots) if slots else 0) + 1
                slots[n] = v
                heading_slots.add(n)
            else:
                slots.setdefault(n, v)  # echo: fill gaps, never override
    return slots, heading_slots


def cmd_rounds(owner, repo, proj_num, proj_id, num, cap, escalate):
    """Count skeptic verdict comments on an issue. Cap NEEDS-REWORK loops:
    after `cap` rework rounds the loop escalates to a human instead of
    cycling silently (same spirit as the self-heal cap). Only verdicts
    posted in a recognized format are counted — a verdict living only in
    a review doc is invisible here (post the heading)."""
    r = gh("api", f"repos/{repo}/issues/{num}/comments",
           "--paginate", "--slurp")
    pages = json.loads(r.stdout)  # slurp: array of per-page arrays
    comments = [c["body"] for page in pages for c in page]
    slots, _ = count_rounds(comments)
    counts = {"PASS": 0, "NEEDS REWORK": 0, "FAIL": 0}
    for v in slots.values():
        counts[v] += 1
    nr = counts["NEEDS REWORK"]
    nxt = (max(slots) if slots else 0) + 1
    print(f"#{num} skeptic rounds: NEEDS_REWORK={nr} PASS={counts['PASS']} "
          f"FAIL={counts['FAIL']} — next review = r{nxt} (cap {cap})")
    if nr >= cap:
        msg = (f"skeptic round cap reached ({nr} NEEDS REWORK >= {cap}) — "
               f"escalate to human; do NOT launch another rework cycle")
        if escalate:
            try:
                set_status(owner, proj_num, proj_id, num, "Blocked")
                print(f"#{num} -> Blocked")
            except SystemExit:
                print("warn: could not set Blocked (issue not on board?)")
            gh("issue", "comment", str(num), "--repo", repo,
               "--body", f"**Round cap:** {msg}")
            print(f"#{num} escalation comment posted")
        print(msg)
        sys.exit(2)


def cmd_fields(owner, proj_id):
    q = """query($id:ID!){node(id:$id){... on ProjectV2{
      fields(first:30){nodes{... on ProjectV2SingleSelectField{
        id name options{id name}} ... on ProjectV2Field{id name}}}}}}"""
    r = gh("api", "graphql", "-f", f"query={q}", "-F", f"id={proj_id}")
    for f in json.loads(r.stdout)["data"]["node"]["fields"]["nodes"]:
        print(f"{f['id']}  {f['name']}")
        for o in f.get("options", []):
            print(f"    {o['id']}  {o['name']}")


def main():
    import argparse
    p = argparse.ArgumentParser(prog="ghp", description=__doc__.splitlines()[0])
    p.add_argument("--owner"); p.add_argument("--repo"); p.add_argument("--project", type=int)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create"); c.add_argument("title")
    c.add_argument("--body"); c.add_argument("--body-file")
    c.add_argument("--status", default="Todo"); c.add_argument("--epic", type=int)

    b = sub.add_parser("board"); b.add_argument("--status")

    s = sub.add_parser("status"); s.add_argument("num", type=int); s.add_argument("name")

    for name, st in (("start", "In Progress"), ("review", "Review"),
                     ("block", "Blocked")):
        x = sub.add_parser(name); x.add_argument("num", type=int); x.set_defaults(_st=st)

    d = sub.add_parser("done"); d.add_argument("num", type=int)
    d.add_argument("--comment-file")

    k = sub.add_parser("check"); k.add_argument("num", type=int); k.add_argument("pattern")
    l = sub.add_parser("link"); l.add_argument("epic", type=int); l.add_argument("task", type=int)

    m = sub.add_parser("comment"); m.add_argument("num", type=int); m.add_argument("--file", required=True)

    r_ = sub.add_parser("rounds"); r_.add_argument("num", type=int)
    r_.add_argument("--cap", type=int, default=6)
    r_.add_argument("--escalate", action="store_true")

    o = sub.add_parser("doc"); o.add_argument("num", type=int); o.add_argument("path")
    o.add_argument("--text")

    sub.add_parser("fields")

    a = p.parse_args()
    owner, repo, proj_num = load_config(a)
    pid = project_id(owner, proj_num)

    if a.cmd == "create":
        cmd_create(owner, repo, proj_num, pid, a)
    elif a.cmd == "board":
        cmd_board(owner, proj_num, a.status)
    elif a.cmd == "status":
        set_status(owner, proj_num, pid, a.num, a.name)
    elif a.cmd in ("start", "review", "block"):
        set_status(owner, proj_num, pid, a.num, a._st)
    elif a.cmd == "done":
        cmd_done(owner, repo, proj_num, pid, a.num, a.comment_file)
    elif a.cmd == "check":
        cmd_check(repo, a.num, a.pattern)
    elif a.cmd == "link":
        cmd_link(repo, a.epic, a.task)
    elif a.cmd == "comment":
        gh("issue", "comment", str(a.num), "--repo", repo, "--body-file", a.file)
        print(f"#{a.num} commented")
    elif a.cmd == "doc":
        cmd_doc(owner, repo, a.num, a.path, a.text)
    elif a.cmd == "rounds":
        cmd_rounds(owner, repo, proj_num, pid, a.num, a.cap, a.escalate)
    elif a.cmd == "fields":
        cmd_fields(owner, pid)


if __name__ == "__main__":
    main()
