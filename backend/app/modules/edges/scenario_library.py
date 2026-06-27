"""Tail-stress scenario library — historical crashes the edge must be red-teamed against.

A small, deterministic registry of the regimes that break momentum: the 2008 GFC, the Mar-2020
COVID crash, and the 2024-25 momentum-factor unwind. Gate-3 surfaces these as red-team lines next
to the Monte-Carlo cone so a pass is never read without the worst historical context beside it.
Shocks are peak-to-trough equity moves (negative %). Pure data, no clock.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    name: str
    equity_shock_pct: float  # peak-to-trough equity move, negative
    note: str = ""


_LIBRARY: tuple[Scenario, ...] = (
    Scenario("gfc_2008", -55.0, "Global Financial Crisis 2008-09, NIFTY ~ -55%"),
    Scenario("covid_mar2020", -38.0, "COVID crash Feb-Mar 2020, NIFTY ~ -38%"),
    Scenario("momentum_2024_25", -31.0, "2024-25 momentum-factor unwind ~ -31%"),
)


def scenarios() -> list[Scenario]:
    return list(_LIBRARY)


def worst_shock() -> float:
    """The deepest historical shock — the red-team floor for Gate-3."""
    return min(s.equity_shock_pct for s in _LIBRARY)
