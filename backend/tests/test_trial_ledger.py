"""Trial-ledger — declare/record/spent/remaining + append-only durability."""

from __future__ import annotations

from pathlib import Path

from app.modules.edges import trial_ledger as tl


def test_declare_record_spent_remaining(tmp_path: Path) -> None:
    p = tmp_path / "trials.jsonl"
    tl.declare_budget("edge-momo", 10, p)
    tl.record_trial("edge-momo", path=p)
    tl.record_trial("edge-momo", n=3, path=p)
    assert tl.budget("edge-momo", p) == 10
    assert tl.spent("edge-momo", p) == 4
    assert tl.remaining("edge-momo", p) == 6


def test_latest_declaration_wins(tmp_path: Path) -> None:
    p = tmp_path / "trials.jsonl"
    tl.declare_budget("e", 5, p)
    tl.declare_budget("e", 8, p)  # a correction is a new line, not an edit
    assert tl.budget("e", p) == 8
    # The original declaration is still on disk (append-only — nothing rewritten).
    assert sum(1 for ln in p.read_text().splitlines() if '"budget"' in ln) == 2


def test_edges_are_isolated(tmp_path: Path) -> None:
    p = tmp_path / "trials.jsonl"
    tl.declare_budget("a", 4, p)
    tl.record_trial("a", path=p)
    tl.record_trial("b", path=p)
    assert tl.spent("a", p) == 1 and tl.spent("b", p) == 1
    assert tl.budget("b", p) == 0


def test_missing_ledger_reads_empty(tmp_path: Path) -> None:
    assert tl.spent("ghost", tmp_path / "absent.jsonl") == 0
    assert tl.remaining("ghost", tmp_path / "absent.jsonl") == 0
