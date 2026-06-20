"""cage_human backfill — one Tier-1 human receipt per task, fail-open + idempotent."""

from __future__ import annotations

import pytest

from alphaforge_anton_llm import cage_human

cage = pytest.importorskip("cage")  # skip if the sibling flux isn't installed
ledger = pytest.importorskip("cage.ledger")
tasks = pytest.importorskip("cage.tasks")


@pytest.fixture
def root(tmp_path, monkeypatch):
    """Redirect the whole Cage ledger (calls/receipts/tasks) to a temp dir."""
    monkeypatch.setenv("CAGE_LEDGER", str(tmp_path / "ledger"))
    return tmp_path


def _human(root):
    return [r for r in ledger.receipts(root) if r.get("tool") == "human"]


def test_one_human_receipt_per_typed_task(root):
    tasks.record(root, "add-broker", type="feature", snapshot=False)
    tasks.record(root, "fix-pnl", type="bugfix", snapshot=False)
    assert cage_human.backfill(root) == 2
    receipts = _human(root)
    assert {r["task"] for r in receipts} == {"add-broker", "fix-pnl"}
    assert {r["meta"]["task_type"] for r in receipts} == {"feature", "bugfix"}


def test_idempotent_rerun_does_not_double_record(root):
    tasks.record(root, "add-broker", type="feature", snapshot=False)
    assert cage_human.backfill(root) == 1
    assert cage_human.backfill(root) == 0  # record_human dedups on (task, call)
    assert len(_human(root)) == 1


def test_typeless_task_falls_to_default_estimated(root):
    tasks.record(root, "mystery", snapshot=False)  # no type
    assert cage_human.backfill(root) == 1
    (r,) = _human(root)
    assert r["method"] == "estimated"  # never "measured" — minutes are not invented
    assert not r["meta"].get("task_type")  # global-default path, no fabricated type


def test_no_tasks_records_nothing(root):
    assert cage_human.backfill(root) == 0
    assert _human(root) == []


def test_receipt_carries_no_pii(root):
    tasks.record(root, "add-broker", type="feature", snapshot=False)
    cage_human.backfill(root)
    (r,) = _human(root)
    # Only task id, type, and the derived shape — no name/comp/account/folio anywhere.
    assert set(r["meta"]) <= {"task_type", "rate_usd_per_hr", "agent"}
    assert r["task"] == "add-broker"
