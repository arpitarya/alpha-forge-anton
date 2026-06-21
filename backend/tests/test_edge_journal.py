"""The discovery journal — every run, pass OR kill, is recorded with its gate stats.

`build_record` is the pure core: it derives `gate_reached` (highest *passed* gate) and
`passed` (all gates passed) from a run's gate results. A KILL is journaled just as a
PASS is — survivorship bias is the bug the journal exists to prevent. `append` is
exercised with a stubbed elgar bridge so the test stays offline (no store, no network).

    uv run pytest tests/test_edge_journal.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.edges import edge_journal
from app.modules.edges.edge_journal import build_record
from app.modules.edges.edge_schema import GateResult, ResultStats

_RUN = datetime(2026, 6, 21, 9, 30, tzinfo=UTC)


def _gate(n: int, passed: bool) -> GateResult:
    return GateResult(gate=n, passed=passed, stats=ResultStats(trades=3, expectancy_pct=1.0))


def test_pass_run_records_both_gates_cleared():
    rec = build_record("edge-1", _RUN, [_gate(1, True), _gate(2, True)])
    assert rec.passed is True
    assert rec.gate_reached == 2
    assert rec.run_at == _RUN.isoformat()


def test_kill_at_gate2_records_gate1_reached_but_not_passed():
    rec = build_record("edge-2", _RUN, [_gate(1, True), _gate(2, False)])
    assert rec.passed is False
    assert rec.gate_reached == 1  # cleared gate 1, killed at gate 2


def test_kill_at_gate1_records_zero_reached():
    rec = build_record("edge-3", _RUN, [_gate(1, False)])
    assert rec.passed is False and rec.gate_reached == 0


@pytest.mark.asyncio
async def test_append_writes_a_doc_through_the_bridge(monkeypatch):
    captured: dict[str, object] = {}

    async def _fake_save(doc_id, content, message=None, collection=None):
        captured.update(id=doc_id, content=content, collection=collection)
        return f"elgar://plan/{doc_id}"

    monkeypatch.setattr(edge_journal.elgar_bridge, "save", _fake_save)
    rec = build_record("edge-4", _RUN, [_gate(1, False)])
    ref = await edge_journal.append(rec)

    assert ref is not None
    assert captured["collection"] == "edges-journal"
    assert "KILL" in captured["content"] and "edge-4" in captured["content"]
