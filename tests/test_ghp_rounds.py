"""Regression suite for ghp.count_rounds — skeptic-round cap counter.

Guards the failure classes found on crypto_trader_v4#56 r1/r2:
same-round heading+echo double-count, echo overriding authoritative
headings, prose false positives, intra-comment ordering steals.
Run: python -m pytest tests/test_ghp_rounds.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ghp import count_rounds


def slots_of(comments):
    return count_rounds(comments)[0]


def test_heading_plus_own_echo_is_one_round():
    assert slots_of([
        "## Skeptic Review — NEEDS REWORK\nfound issues",
        "Skeptic r1 NEEDS REWORK — rework pushed in abc123",
    ]) == {1: "NEEDS REWORK"}


def test_echo_cannot_override_numbered_heading():
    assert slots_of([
        "## Skeptic Review r2 — PASS",
        "Skeptic r2 NEEDS REWORK — rework pushed",
    ]) == {2: "PASS"}


def test_stray_pass_echo_cannot_erase_nr_heading():
    # cap must not fail to trip because of a stray later mention
    assert slots_of([
        "## Skeptic Review r2 — NEEDS REWORK",
        "note: skeptic r2 PASS was the wrong call",
    ]) == {2: "NEEDS REWORK"}


def test_prose_mentions_do_not_count():
    assert slots_of(["the skeptic review - pass criteria are unclear"]) == {}
    assert slots_of(["I think skeptic r2 NEEDS REWORK is wrong"]) == {}
    assert slots_of(["mid-line x ## Skeptic Review — FAIL"]) == {}


def test_unnumbered_heading_after_echoes_is_a_new_round():
    assert slots_of([
        "Skeptic r1 NEEDS REWORK — pushed",
        "## Skeptic Review — PASS",
    ]) == {1: "NEEDS REWORK", 2: "PASS"}


def test_echo_only_rounds_fill_gaps():
    assert slots_of([
        "Skeptic r1 NEEDS REWORK",
        "Skeptic r2 NEEDS REWORK",
        "Skeptic r3 PASS",
    ]) == {1: "NEEDS REWORK", 2: "NEEDS REWORK", 3: "PASS"}


def test_intra_comment_textual_order_no_slot_steal():
    # final verdict comment recapping a doc-only r3 verdict, then its own
    # unnumbered heading — heading must take a NEW slot, not r3's
    assert slots_of([
        "Skeptic r1 NEEDS REWORK",
        "Skeptic r2 NEEDS REWORK",
        "Skeptic r3 NEEDS REWORK\n\n## Skeptic Review — PASS",
    ]) == {1: "NEEDS REWORK", 2: "NEEDS REWORK", 3: "NEEDS REWORK",
           4: "PASS"}


def test_fenced_verdict_templates_do_not_count():
    assert slots_of([
        "use this format:\n```\n## Skeptic Review r1 — PASS\n```",
    ]) == {}


def test_case_and_separator_variants():
    assert slots_of([
        "## skeptic review r1 - needs rework",
        "Skeptic r2 fail",
    ]) == {1: "NEEDS REWORK", 2: "FAIL"}


def test_empty_and_unrelated_comments():
    assert slots_of([]) == {}
    assert slots_of(["just a normal comment", "another one"]) == {}
