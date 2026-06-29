"""Watch-stage logic — deterministic decay detection and the decay-kill.

`analyze` turns a realized series into decay signals ($0, no LLM): realized expectancy
collapsing vs what the edge was approved on, a cumulative drawdown breaching the -12 / -20
guard, or a losing streak. The verdict gates a decay-kill recommendation. `retire` journals a
`RetirementRecord` to elgar (fail-loud, PII-guarded reason) — the frozen spec is never mutated.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.concierge import critic_guard
from app.modules.flow.flow_watch_schema import (
    DecaySeverity,
    DecaySignal,
    Observation,
    RetirementRecord,
    WatchState,
    WatchVerdict,
)
from app.modules.plans import elgar_bridge

SOFT_PCT = -12.0
HARD_PCT = -20.0
_COLLECTION = "decisions"
_HIGH, _MED = DecaySeverity.HIGH, DecaySeverity.MED


class DecayKillError(ValueError):
    """A decay-kill reason failed the deterministic PII guard — never reaches elgar."""


def _max_drawdown(returns: list[float]) -> float:
    peak = cum = dd = 0.0
    for r in returns:
        cum += r
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return round(dd, 2)


def _streak(returns: list[float]) -> int:
    best = run = 0
    for r in returns:
        run = run + 1 if r < 0 else 0
        best = max(best, run)
    return best


def _signals(exp: float, expected: float, dd: float, streak: int) -> list[DecaySignal]:
    out: list[DecaySignal] = []
    add = lambda sev, name, detail: out.append(DecaySignal(severity=sev, name=name, detail=detail))  # noqa: E731
    if exp < 0:
        add(_HIGH, "expectancy negative", f"realized {exp:.2f}% per period")
    elif expected > 0 and exp < expected * 0.5:
        add(_MED, "expectancy decayed", f"realized {exp:.2f}% vs expected {expected:.2f}%")
    if dd <= HARD_PCT:
        add(_HIGH, "drawdown breach", f"max drawdown {dd:.1f}% past the -20% guard")
    elif dd <= SOFT_PCT:
        add(_MED, "drawdown soft breach", f"max drawdown {dd:.1f}% past the -12% guard")
    if streak >= 5:
        add(_HIGH, "losing streak", f"{streak} consecutive losing periods")
    elif streak >= 3:
        add(_MED, "losing streak", f"{streak} consecutive losing periods")
    return out


def analyze(observations: list[Observation], expected: float) -> WatchState:
    """Deterministic decay read-back — realized stats, signals, and the kill verdict."""
    rets = [o.return_pct for o in observations]
    n = len(rets)
    exp = round(sum(rets) / n, 2) if n else 0.0
    dd = _max_drawdown(rets)
    signals = _signals(exp, expected, dd, _streak(rets))
    highs = sum(s.severity == _HIGH for s in signals)
    meds = sum(s.severity == _MED for s in signals)
    verdict = (WatchVerdict.DECAYED if highs or meds >= 2
               else WatchVerdict.DECAYING if meds else WatchVerdict.HEALTHY)
    return WatchState(
        n_periods=n, realized_expectancy=exp, max_dd=dd, expected_expectancy=expected,
        hit_rate=round(sum(r > 0 for r in rets) / n, 4) if n else 0.0,
        signals=signals, verdict=verdict, kill_recommended=verdict == WatchVerdict.DECAYED,
    )


async def retire(edge_id: str, reason: str, state: WatchState) -> RetirementRecord:
    """Journal a decay-kill to elgar (fail-loud). PII-guard the free-text reason first."""
    if (block := critic_guard.pii_block(reason)) is not None:
        raise DecayKillError(block)
    now = datetime.now(UTC).isoformat()
    rec = RetirementRecord(edge_id=edge_id, reason=reason, max_dd=state.max_dd,
                           realized_expectancy=state.realized_expectancy, retired_at=now)
    doc = (f"---\nedge: {edge_id}\ndecision: retired\nretired_at: {now}\nsource: orff-flow\n---\n"
           f"# RETIRED — {edge_id}\n\n> decayed: {reason}\n\n"
           f"```json\n{rec.model_dump_json(indent=2)}\n```\n")
    rec.ref = await elgar_bridge.save(f"{edge_id}-retired", doc,
                                      message=f"orff: retire {edge_id}", collection=_COLLECTION)
    return rec
