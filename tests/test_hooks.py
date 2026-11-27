"""Regression tests for the plugin lifecycle hook surface."""
import json
from pathlib import Path


def load_hooks():
    hooks_path = Path(__file__).resolve().parent.parent / "hooks.json"
    return json.loads(hooks_path.read_text(encoding="utf-8"))


def test_no_stop_prompt_hook():
    hooks = load_hooks()
    assert "Stop" not in hooks


def test_only_command_hooks_registered():
    hooks = load_hooks()
    hook_types = [
        hook.get("type")
        for groups in hooks.values()
        for group in groups
        for hook in group.get("hooks", [])
    ]
    assert hook_types
    assert set(hook_types) == {"command"}


def test_user_prompt_submit_hook_remains():
    hooks = load_hooks()
    assert "UserPromptSubmit" in hooks
