"""Tests for ghp.analyze_board — pure board-hygiene analysis.

The janitor exists because board cleanup was manual (issue #272 in
opencart3shop): closed issues kept active statuses, open duplicates
appeared from parallel sessions, and review items aged invisibly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ghp import analyze_board, _norm_title

NOW = 1795800000.0  # fixed epoch for deterministic age math
DAY = 86400


def item(num, status, title=None):
    return {"content": {"number": num, "title": title or f"t{num}"},
            "status": status}


def iso_days_ago(days):
    import datetime
    ts = datetime.datetime.fromtimestamp(NOW - days * DAY,
                                         datetime.timezone.utc)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def issue(num, state, days=0, title=""):
    return {"state": state, "updatedAt": iso_days_ago(days),
            "title": title or f"t{num}"}


def test_closed_with_active_status_flagged():
    items = [item(1, "In Progress")]
    issues = {1: issue(1, "CLOSED")}
    f = analyze_board(items, issues, NOW)
    assert f["closed_not_done"] == [(1, "In Progress", "t1")]


def test_closed_without_status_flagged():
    items = [item(1, "")]
    issues = {1: issue(1, "CLOSED")}
    f = analyze_board(items, issues, NOW)
    assert f["closed_not_done"] == [(1, "-", "t1")]


def test_closed_done_is_clean():
    items = [item(1, "Done")]
    issues = {1: issue(1, "CLOSED")}
    f = analyze_board(items, issues, NOW)
    assert not any(f.values())


def test_open_without_status_flagged_but_not_stale():
    items = [item(1, "")]
    issues = {1: issue(1, "OPEN", days=100)}
    f = analyze_board(items, issues, NOW)
    assert f["open_no_status"] == [(1, "t1")]
    assert not f["stale_active"]  # no status -> not an active-status item


def test_open_todo_is_clean():
    items = [item(1, "Todo")]
    issues = {1: issue(1, "OPEN", days=100)}
    f = analyze_board(items, issues, NOW)
    assert not any(f.values())


def test_stale_in_review_after_threshold():
    items = [item(1, "In review")]
    issues = {1: issue(1, "OPEN", days=20)}
    f = analyze_board(items, issues, NOW, stale_days=14)
    assert f["stale_active"] == [(1, "In review", 20, "t1")]


def test_fresh_in_progress_not_stale():
    items = [item(1, "In Progress")]
    issues = {1: issue(1, "OPEN", days=3)}
    f = analyze_board(items, issues, NOW, stale_days=14)
    assert not f["stale_active"]


def test_stale_blocked_flagged():
    items = [item(1, "Blocked")]
    issues = {1: issue(1, "OPEN", days=30)}
    f = analyze_board(items, issues, NOW)
    assert f["stale_active"]


def test_duplicate_open_titles_grouped():
    items = [item(1, "Todo", "fix: same thing"),
             item(2, "In Progress", "Fix: same thing!"),
             item(3, "Todo", "other")]
    issues = {n: issue(n, "OPEN", title=t)
              for n, t in [(1, "fix: same thing"), (2, "Fix: same thing!"),
                           (3, "other")]}
    f = analyze_board(items, issues, NOW)
    assert f["dup_open_titles"] == [("fix same thing", [1, 2])]


def test_duplicate_titles_only_count_open():
    items = [item(1, "Done", "x"), item(2, "Todo", "x")]
    issues = {1: issue(1, "CLOSED", title="x"), 2: issue(2, "OPEN", title="x")}
    f = analyze_board(items, issues, NOW)
    # #1 is closed -> excluded from open-title grouping (but no other findings)
    assert not f["dup_open_titles"]


def test_cross_repo_items_ignored():
    items = [item(999, "In Progress")]
    issues = {}  # not in this repo's issue list
    f = analyze_board(items, issues, NOW)
    assert not any(f.values())


def test_norm_title_punctuation_insensitive():
    assert _norm_title("Fix: A/B!") == _norm_title("fix a b")


def test_unparseable_updated_at_not_stale():
    items = [item(1, "In Progress")]
    iss = {1: {"state": "OPEN", "updatedAt": "garbage", "title": "t1"}}
    f = analyze_board(items, iss, NOW)
    assert not f["stale_active"]
