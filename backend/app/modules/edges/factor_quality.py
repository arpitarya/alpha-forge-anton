"""Quality overlay — keep only ROCE ≥ θ_roce AND debt/equity ≤ θ_de.

The fundamentals feed isn't wired yet, so this is **honest-pending by construction**: a symbol
whose ROCE or D/E is unknown is returned in `pending`, never silently kept (faking a pass) and
never silently dropped without a trace. `quality_filter` returns `(kept, pending)` so the funnel
can report exactly how much of the sleeve could not be quality-screened. `FixtureFundamentals`
serves a committed offline fixture; a real provider implements the same `FundamentalsProvider`.
"""

from __future__ import annotations

from typing import Protocol

from app.modules.edges.factor_schema import FactorConfig


class FundamentalsProvider(Protocol):
    def roce(self, symbol: str) -> float | None: ...
    def debt_equity(self, symbol: str) -> float | None: ...


def quality_filter(
    symbols: list[str], cfg: FactorConfig, fund: FundamentalsProvider
) -> tuple[list[str], list[str]]:
    """(kept, pending). pending = unknown fundamentals — honest-pending, never faked or hidden."""
    kept: list[str] = []
    pending: list[str] = []
    for s in symbols:
        roce, de = fund.roce(s), fund.debt_equity(s)
        if roce is None or de is None:
            pending.append(s)
        elif roce >= cfg.theta_roce and de <= cfg.theta_de:
            kept.append(s)
    return kept, pending


class FixtureFundamentals:
    """Offline fundamentals from two committed dicts; a missing key is honest-pending (None)."""

    def __init__(self, roce: dict[str, float], debt_equity: dict[str, float]) -> None:
        self._roce = roce
        self._de = debt_equity

    def roce(self, symbol: str) -> float | None:
        return self._roce.get(symbol)

    def debt_equity(self, symbol: str) -> float | None:
        return self._de.get(symbol)
