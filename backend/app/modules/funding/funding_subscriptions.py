"""Load the fixed-cost subscriptions registry → monthly opex in INR.

The registry (`subscriptions.toml`) is the deterministic denominator of the self-funding
test: `Objective.self_funding.covered` is true when realized savings/P&L ≥ this opex. Each
row is normalized to INR via the shared `brokers.fx.to_inr` and to a monthly cadence
(annual ÷ 12), so the figure is comparable to a monthly realized-P&L target.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel

from app.modules.brokers.fx import to_inr
from app.modules.contracts.objective_contract import SelfFunding

_DEFAULT_PATH = Path(__file__).parent / "subscriptions.toml"
_MONTHS = {"monthly": 1.0, "annual": 1.0 / 12.0}


class Subscription(BaseModel):
    name: str
    amount: float = 0.0
    currency: str = "INR"
    cadence: str = "monthly"

    def monthly_inr(self) -> float:
        """This subscription's cost as INR per month."""
        return to_inr(self.amount, self.currency) * _MONTHS.get(self.cadence, 1.0)


def load_subscriptions(path: Path | None = None) -> list[Subscription]:
    """Parse the registry; an absent file is an empty registry (zero opex), not an error."""
    p = path or _DEFAULT_PATH
    if not p.exists():
        return []
    data = tomllib.loads(p.read_text(encoding="utf-8"))
    return [Subscription(**row) for row in data.get("sub", [])]


def opex_per_month(path: Path | None = None) -> float:
    """Total fixed opex, INR/month — feeds Objective.self_funding.opex_per_month."""
    return round(sum(s.monthly_inr() for s in load_subscriptions(path)), 2)


def self_funding(
    reserve: float = 0.0, cage_savings_per_month: float = 0.0, path: Path | None = None
) -> SelfFunding:
    """Build the self-funding line. `covered` stays None (honest-pending) until a realised-P&L
    source exists (Gate-4 paper) — cage savings reduce opex, they are not income."""
    return SelfFunding(
        opex_per_month=opex_per_month(path),
        cage_savings_per_month=cage_savings_per_month,
        reserve=reserve,
        covered=None,
    )
