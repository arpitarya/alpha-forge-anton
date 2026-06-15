"""`just backtest` entry — replay the active config over real cached history (§10.5).

Thin CLI: run the engine, print the after-cost report with a loud go/no-go verdict
so a config without an edge is obvious. Always exits 0 — it reports, it doesn't
gate. Reproducible: historical bars + the disk cache mean reruns match.

    just backtest   |   uv run python -m app.modules.signals.backtest_cli
"""

from __future__ import annotations

import asyncio

from app.modules.signals.backtest import run_backtest
from app.modules.signals.backtest_schema import BacktestReport


def render(r: BacktestReport) -> str:
    lines = [
        f"\n── Backtest (config {r.config_hash}, {r.period}, {r.universe_size} symbols)",
        f"  trades {r.trades}  win-rate {r.win_rate:.0%}  profit-factor {r.profit_factor}",
        f"  gross ₹{r.gross:,.0f}  net-after-costs ₹{r.net:,.0f}",
        f"  expectancy ₹{r.expectancy_inr:,.0f}/trade ({r.expectancy_pct:+.2f}%)",
        f"  max drawdown ₹{r.max_drawdown:,.0f} ({r.max_drawdown_pct:.1f}%)",
        *[f"  note: {n}" for n in r.notes],
    ]
    verdict = ("✅ POSITIVE expectancy after costs" if r.positive_expectancy
               else "❌ NOT positive after costs — do not size up")
    return "\n".join(lines) + f"\n\n{verdict}"


async def _amain() -> int:
    print(render(await run_backtest()))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_amain()))
