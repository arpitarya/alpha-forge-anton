"""Watch stage — deterministic decay detection + the decay-kill (elgar write mocked).

Pins the decay engine: a healthy series stays HEALTHY (no kill); a series with negative realized
expectancy / a -20% drawdown / a losing streak DECAYS and recommends a kill; signals are
severity-tagged; the decay-kill PII-guards its reason before journaling to elgar; and Watch
unlocks only on a PASS. No real store write.

    uv run pytest tests/test_flow_watch.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.edges.edge_journal import JournalRecord
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.flow import flow_watch
from app.modules.flow.flow_schema import StageId, StageState
from app.modules.flow.flow_stages import derive
from app.modules.flow.flow_watch_schema import (
    DecaySeverity,
    Observation,
    RetirementRecord,
    WatchVerdict,
)


def _obs(returns: list[float]) -> list[Observation]:
    return [Observation(period=f"w{i}", return_pct=r) for i, r in enumerate(returns)]


def test_healthy_series_does_not_recommend_a_kill():
    st = flow_watch.analyze(_obs([3, 2, 4, 1]), expected=2.0)
    assert st.verdict == WatchVerdict.HEALTHY and not st.kill_recommended
    assert st.realized_expectancy == 2.5 and st.signals == []


def test_decayed_series_recommends_a_kill_with_high_signals():
    st = flow_watch.analyze(_obs([-3, -4, -5, -2, -6]), expected=2.0)
    assert st.verdict == WatchVerdict.DECAYED and st.kill_recommended
    assert st.max_dd == -20.0  # cumulative -20%
    names = {s.name for s in st.signals if s.severity == DecaySeverity.HIGH}
    assert {"expectancy negative", "drawdown breach", "losing streak"} <= names


def test_two_med_signals_decay_without_a_high():
    # expectancy decayed (MED) + a 3-streak (MED), no HIGH → DECAYED on 2 MED
    st = flow_watch.analyze(_obs([0.5, -1, -1, -1, 5]), expected=4.0)
    assert sum(s.severity == DecaySeverity.MED for s in st.signals) >= 2
    assert st.verdict == WatchVerdict.DECAYED


@pytest.mark.asyncio
async def test_decay_kill_pii_guards_reason_then_journals(monkeypatch):
    async def _save(*a, **k) -> str:
        return "elgar://plan/edge-x-retired"

    monkeypatch.setattr(flow_watch.elgar_bridge, "save", _save)
    state = flow_watch.analyze(_obs([-3, -4, -5, -2, -6]), 2.0)
    with pytest.raises(flow_watch.DecayKillError, match="hard identifier"):
        await flow_watch.retire("edge-x", "see PAN ABCDE1234F", state)
    rec = await flow_watch.retire("edge-x", "expectancy collapsed", state)
    assert isinstance(rec, RetirementRecord) and rec.ref and rec.max_dd == -20.0


def test_watch_unlocks_only_on_a_pass():
    spec = EdgeSpec(
        id="e",
        hypothesis="h",
        signal="momentum",
        pre_registered_at=datetime(2026, 6, 1, tzinfo=UTC),
    )
    def watch_state(passed: bool | None) -> StageState:
        rec = None if passed is None else JournalRecord(
            edge_id="e", run_at="2026-06-27T00:00:00Z", gate_reached=3, passed=passed)
        return {s.id: s for s in derive(spec, rec)}[StageId.WATCH].state

    assert watch_state(True) == StageState.ACTIVE
    assert watch_state(False) == StageState.BLOCKED
    assert watch_state(None) == StageState.NA
