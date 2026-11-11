#!/usr/bin/env python3
"""ps1-encoding gate — PreToolUse hook for `write`/`edit` tools.

Blocks non-ASCII content written to Windows script files
(.ps1/.bat/.cmd/.vbs): PowerShell 5.1 parses BOM-less files as ANSI
and cmd.exe batch files are ANSI/OEM, so Cyrillic/unicode content
arrives as mojibake and breaks the parser — failure class F-005
(opencart3 journal), ps1-encoding skill.

Wire-up: repo `.devin/hooks.v1.json` ->
    {"matcher": "^(write|edit)$", "hooks": [{"type": "command",
      "command": "python <abs path>/ps1_gate.py", "timeout": 10}]}
See templates/project-local/hooks.v1.json.

stdin: {"tool_name": "write"|"edit",
        "tool_input": {"file_path": ..., "content" | "new_string": ...}}
exit 0 = allow; exit 2 = block (stderr is shown back to the agent).

Bypass: include the literal marker `GATE_PS1=off` in the payload (a
comment works) — explicit acknowledgment, e.g. when a follow-up step
rewrites the file to UTF-8 BOM. Files produced via `exec` (e.g.
`Set-Content -Encoding utf8`) never reach this gate anyway.
"""

import json
import os
import sys

BYPASS = "GATE_PS1=off"
EXTS = {".ps1", ".bat", ".cmd", ".vbs"}

REMEDY = (
    "ps1-encoding gate: non-ASCII content in a Windows script "
    "(.ps1/.bat/.cmd/.vbs). PS 5.1 parses BOM-less files as ANSI; "
    "cmd.exe is ANSI/OEM — the script arrives corrupted (F-005).\n"
    "Write it ASCII-only, or produce the file via exec with a BOM:\n"
    "  - PowerShell: Set-Content -Encoding utf8 <file>\n"
    "  - python:     open(f, 'w', encoding='utf-8-sig')\n"
    "If the non-ASCII is intentional (e.g. a later BOM rewrite), add a "
    "comment containing GATE_PS1=off to the payload."
)


def tool_text(name, ti):
    if name == "write":
        return ti.get("content") or ""
    if name == "edit":
        return ti.get("new_string") or ""
    return ""


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0  # can't parse -> don't gate what we can't see
    ti = data.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if os.path.splitext(path)[1].lower() not in EXTS:
        return 0
    text = tool_text(data.get("tool_name") or "", ti)
    if BYPASS in text or all(ord(c) < 128 for c in text):
        return 0
    print(REMEDY, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
