"""Null-data self-test — the standing trust check that the funnel finds no fake edge.

Feeds seeded, zero-drift random walks through the funnel and asserts **no edge** (a funnel
that finds an edge in noise is broken/overfit). `Funnel` is the interface later phases
implement; the default `GateFunnel` composes the *existing* gates into a `TestReport`.
Run:  just null-data   |   uv run python -m app.modules.edges.null_selftest
"""

from __future__ import annotations

import asyncio
import random
from datetime import UTC, datetime
from typing import Protocol

from app.modules.contracts.testreport_contract import TestReport, Walkforward
from app.modules.edges.edge_backtest import run_gate1
from app.modules.edges.edge_data import Bars, BarsProvider
from app.modules.edges.edge_schema import EdgeSpec, GateResult
from app.modules.edges.edge_walkforward import run_gate2

_PRE = datetime(2000, 1, 1, tzinfo=UTC)  # safely pre-dates any run (pre-registration ok)


class Funnel(Protocol):
    async def run(self, bars: Bars) -> TestReport: ...


def _dates(n: int) -> list[str]:
    return [f"2020-{i // 28 % 12 + 1:02d}-{i % 28 + 1:02d}" for i in range(n)]


def random_walk_bars(seed: int, n: int = 320) -> Bars:
    """A seeded, zero-drift multiplicative random walk — deterministic, no real signal."""
    rng = random.Random(seed)  # noqa: S311 — synthetic test data, not cryptographic
    price, closes = 1000.0, []
    for _ in range(n):
        price *= 1.0 + rng.uniform(-0.02, 0.02)
        closes.append(round(price, 4))
    return Bars(dates=_dates(n), close=closes)


class _OneSymbol:
    def __init__(self, bars: Bars) -> None:
        self._bars = bars

    async def bars(self, symbol: str, years: int) -> Bars:
        return self._bars


class GateFunnel:
    """Default funnel — composes the existing edge gates into a TestReport (no new logic)."""

    def __init__(self, signal: str = "momentum") -> None:
        self._signal = signal

    async def run(self, bars: Bars) -> TestReport:
        provider: BarsProvider = _OneSymbol(bars)
        spec = EdgeSpec(
            id="null",
            hypothesis="null-data",
            universe=["NULL"],
            signal=self._signal,
            holding_period_days=5,
            pre_registered_at=_PRE,
        )
        gates: list[GateResult] = [await run_gate1(spec, provider)]
        if gates[0].passed:
            gates.append(await run_gate2(spec, provider))
        wf = gates[1] if len(gates) > 1 else None
        positive = sum(1 for w in wf.windows if w.expectancy_pct > 0) if wf and wf.windows else 0
        return TestReport(
            edge_id=spec.id,
            gates_passed=[g.gate for g in gates if g.passed],
            walkforward=Walkforward(
                agg_calmar=wf.stats.calmar if wf else 0.0,
                pct_windows_positive=positive / len(wf.windows) if wf and wf.windows else 0.0,
            ),
            verdict="pass" if gates and all(g.passed for g in gates) else "fail",
            pre_registered_at=spec.pre_registered_at,
        )


async def run_null_selftest(trials: int = 25, funnel: Funnel | None = None) -> int:
    """Feed `trials` seeded random series through the funnel; return how many it flagged."""
    f = funnel or GateFunnel()
    reports = [await f.run(random_walk_bars(seed)) for seed in range(trials)]
    return sum(1 for r in reports if r.verdict == "pass")


def main() -> int:
    found = asyncio.run(run_null_selftest(25))
    ok = found == 0
    verdict = "finds NO edge ✅" if ok else f"flagged {found} spurious edge(s) ❌"
    print(f"null-data: 25 random series → {found} false edge(s) — {verdict}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
