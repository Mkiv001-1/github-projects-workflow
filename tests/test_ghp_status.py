"""Tests for ghp.resolve_status — alias/candidate status resolution.

Boards name the same concept differently ("Todo" vs "Backlog",
"Review" vs "In review"); a single alias->name map broke on foreign
boards (F-017 class). Candidates are tried in order: literal name
first, then the alias preference list.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ghp import resolve_status

TODO_BOARD = {"todo": "id-todo", "in progress": "id-wip", "done": "id-done"}
BACKLOG_BOARD = {"backlog": "id-back", "in progress": "id-wip",
                 "in review": "id-rev", "done": "id-done"}


def test_literal_name_matches_its_own_board():
    assert resolve_status(TODO_BOARD, "todo") == "id-todo"
    assert resolve_status(BACKLOG_BOARD, "backlog") == "id-back"


def test_todo_alias_falls_through_to_backlog_board():
    assert resolve_status(BACKLOG_BOARD, "todo") == "id-back"


def test_backlog_alias_falls_through_to_todo_board():
    assert resolve_status(TODO_BOARD, "backlog") == "id-todo"


def test_review_resolves_in_review_option():
    assert resolve_status(BACKLOG_BOARD, "review") == "id-rev"


def test_wip_alias():
    assert resolve_status(TODO_BOARD, "wip") == "id-wip"


def test_unique_prefix_match():
    assert resolve_status(TODO_BOARD, "don") == "id-done"


def test_single_hit_prefix_is_forgiving():
    # "in" -> "in progress" is a deliberate forgiving match
    assert resolve_status(TODO_BOARD, "in") == "id-wip"


def test_ambiguous_prefix_returns_none():
    both = {"in progress": "a", "in review": "b"}
    assert resolve_status(both, "in") is None


def test_unknown_status_returns_none():
    assert resolve_status(TODO_BOARD, "bogus") is None
