#!/usr/bin/env python3
"""rsi_safe_gate — PreToolUse hook protecting the autoresearch "safe".

Blocks agent access to the parts of an RSI/autoresearch loop that must
stay out of its reach (canon: docs/rsi-autoresearch.md, rule 2 "Safe"):

  * write/edit  -> anything under autoresearch/eval/ or
                   autoresearch/holdout/            -> BLOCK
  * read        -> anything under autoresearch/holdout/ -> BLOCK
  * write/edit  -> autoresearch/journal.md allowed
                   (append-only by convention; the loop needs it)
  * anything outside autoresearch/                  -> allow

Wire-up: repo `.devin/hooks.v1.json` ->
    {"matcher": "^(write|edit|read)$", "hooks": [{"type": "command",
      "command": "python <abs path>/rsi_safe_gate.py", "timeout": 10}]}

stdin: {"tool_name": "write"|"edit"|"read",
        "tool_input": {"file_path": ...}}
exit 0 = allow; exit 2 = block (stderr is shown back to the agent).

Limitations (same class as ps1_gate): file tools only — a determined
`exec` call can still write eval/. The gate is a guardrail against
accidental/habitual edits, not a sandbox. Bypass marker for humans:
literal `GATE_RSI=off` in the payload comment.
"""

import json
import os
import sys

BYPASS = "GATE_RSI=off"

REMEDY = (
    "rsi_safe_gate: {path} is inside the autoresearch SAFE zone.\n"
    "  - autoresearch/eval/    read-only oracle; the loop may RUN\n"
    "                          run_eval but never edit it.\n"
    "  - autoresearch/holdout/ data the agent must not see at all.\n"
    "Goodhart: optimizing the number by touching the meter is failure,\n"
    "not progress (canon: docs/rsi-autoresearch.md).\n"
    "If a human explicitly asked for this change, add a comment with\n"
    "GATE_RSI=off to the payload, or edit outside the agent session."
)


def norm(p):
    return os.path.normpath(p).replace("\\", "/").lower()


def under(path, marker):
    """True if path contains an autoresearch/<marker>/ component."""
    parts = norm(path).split("/")
    for i, part in enumerate(parts):
        if part == "autoresearch" and i + 1 < len(parts) and parts[i + 1] == marker:
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0  # can't parse -> don't gate what we can't see

    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if not path:
        return 0

    payload = " ".join(str(ti.get(k) or "") for k in ("content", "new_string", "old_string"))
    if BYPASS in payload:
        return 0

    if tool in ("write", "edit"):
        if under(path, "eval") or under(path, "holdout"):
            print(REMEDY.format(path=path), file=sys.stderr)
            return 2
    elif tool == "read":
        if under(path, "holdout"):
            print(REMEDY.format(path=path), file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
