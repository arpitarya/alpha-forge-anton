"""Forward projections on committed capital-market assumptions.

Rates come from one auditable source — the `capital-market-assumptions` Fux entry
(percentages only, git-safe); personal figures (initial corpus, SIP) arrive per
request and are never persisted. Mix rate = plan targets weighted by class assumptions, so a
projection is always consistent with the active plan in the elgar store.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from app.modules.plans.plan_loader import load_plan

_ENTRY = Path(__file__).resolve().parents[4] / ".fux" / "rules" / "capital-market-assumptions.md"
_YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)


@lru_cache(maxsize=1)
def assumptions() -> dict:
    """{expected_return_pa: {class: pct}, inflation_pa} from the committed Fux entry."""
    match = _YAML_BLOCK.search(_ENTRY.read_text(encoding="utf-8"))
    if not match:
        raise ValueError("capital-market-assumptions: no ```yaml block")
    raw = yaml.safe_load(match.group(1)) or {}
    return {
        "expected_return_pa": {str(k): float(v)
                               for k, v in (raw.get("expected_return_pa") or {}).items()},
        "inflation_pa": float(raw.get("inflation_pa", 0.0)),
    }


def rate_for(asset_class: str | None, plan_id: str = "core-allocation") -> float:
    """Expected nominal return %pa — a single class, or the plan-weighted mix."""
    rates = assumptions()["expected_return_pa"]
    if asset_class:
        if asset_class not in rates:
            raise ValueError(f"no assumption for asset class {asset_class!r}")
        return rates[asset_class]
    targets = load_plan(plan_id).targets
    return round(sum(rates.get(cls.value, 0.0) * pct for cls, pct in targets.items()) / 100, 2)


def project(initial: float, monthly: float, years: int,
            asset_class: str | None = None, plan_id: str = "core-allocation") -> dict:
    """Yearly nominal + inflation-adjusted series for a lump sum + monthly SIP."""
    rate = rate_for(asset_class, plan_id)
    infl = assumptions()["inflation_pa"]
    r_m = (1 + rate / 100) ** (1 / 12) - 1
    nominal, real, value = [], [], float(initial)
    for year in range(1, years + 1):
        for _ in range(12):
            value = value * (1 + r_m) + monthly
        nominal.append(round(value, 2))
        real.append(round(value / (1 + infl / 100) ** year, 2))
    return {
        "rate_pa": rate,
        "inflation_pa": infl,
        "asset_class": asset_class or f"plan:{plan_id}",
        "years": list(range(1, years + 1)),
        "nominal": nominal,
        "real": real,
        "assumptions_ref": "fux why capital-market-assumptions",
    }
