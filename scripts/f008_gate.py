#!/usr/bin/env python3
"""F-008 gate — PreToolUse hook for the `exec` tool.

Blocks `wsl ... -c` / nested-shell commands whose payload carries shell
metacharacters OUTSIDE single quotes (backtick, $(, ${, <<). The outer
shell expands them before the inner `-c` string ever reaches bash —
the failure class that corrupted GitHub payloads and once deleted a
project .venv (92 recorded instances across C:\\git failure journals,
class F-008).

Wire-up: repo `.devin/hooks.v1.json` ->
    {"matcher": "^exec$", "hooks": [{"type": "command",
      "command": "python <abs path>/f008_gate.py", "timeout": 10}]}
See templates/project-local/hooks.v1.json.

stdin: {"tool_name": "exec", "tool_input": {"command": "..."}}
exit 0 = allow; exit 2 = block (stderr is shown back to the agent).

Bypass: put GATE_F008=off into the command (e.g. as an env prefix) —
an explicit acknowledgment that the metacharacters are intentional.
"""

import json
import re
import sys

BYPASS = "GATE_F008=off"
WSL_RE = re.compile(r"(?:^|[|&;>\s])wsl(?:\.exe)?(?:\s|$)")
NESTED_C_RE = re.compile(r"(?:wsl(?:\.exe)?|\bbash\b|\bsh\b)[^|&;\n]*\s-c\b")

REMEDY = (
    "F-008 gate: shell metacharacters (`  $(  ${  $VAR  <<) outside single "
    "quotes in a `wsl ... -c` command are expanded by the OUTER shell "
    "before bash sees them — payloads get corrupted or executed.\n"
    "Run the payload as a FILE instead:\n"
    "  - write it under _tmp/ or %TEMP%, then: wsl bash _tmp/payload.sh\n"
    "  - gh ... --body-file <file>   or   gh api -F body=@<file>\n"
    "  - or: bash .devin/scripts/wsl-run.sh <file> [args]  (if vendored)\n"
    "Prefix the command with GATE_F008=off only when the metacharacters "
    "are intentional (e.g. a deliberate outer-shell substitution)."
)


def _is_dollar_expansion(cmd, i):
    nxt = cmd[i + 1:i + 2]
    return bool(nxt) and (nxt in "({" or nxt.isalpha() or nxt == "_")


def has_unsafe_metachars(cmd):
    """True when `, $(, ${, $VAR, or << appear outside single-quoted
    regions.

    POSIX rule the gate encodes: the outer shell expands `, $(, ${,
    $VAR in double-quoted and bare text, but NOT inside single quotes —
    so a fully single-quoted `wsl bash -c '...'` is safe to pass through.
    """
    sq = dq = False
    i, n = 0, len(cmd)
    while i < n:
        ch = cmd[i]
        if sq:
            if ch == "'":
                sq = False
            i += 1
            continue
        if dq:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                dq = False
            elif ch == "`" or (ch == "$" and _is_dollar_expansion(cmd, i)):
                return True
            i += 1
            continue
        if ch == "'":
            sq = True
        elif ch == '"':
            dq = True
        elif ch == "`":
            return True
        elif ch == "$" and _is_dollar_expansion(cmd, i):
            return True
        elif ch == "<" and cmd[i + 1:i + 2] == "<":
            return True
        i += 1
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0  # can't parse -> don't gate what we can't see
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if BYPASS in cmd or not WSL_RE.search(cmd) or not NESTED_C_RE.search(cmd):
        return 0
    if not has_unsafe_metachars(cmd):
        return 0
    print(REMEDY, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
