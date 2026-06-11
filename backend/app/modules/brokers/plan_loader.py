"""Load a committed Fux plan entry into typed rebalance targets.

A plan lives at `.fux/rules/<plan_id>.plan.md` as **strategy only** — target
percentages and drift bands, never personal figures (see the `secure-holdings-plan`
Fux entry). This reads the fenced ```yaml block and maps it onto `AssetClass`, so the
plan plane drives `HoldingsAggregator.rebalance()` without holdings ever leaving the
machine. Config-load style (sync), matching `app.core.env_loader`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from app.modules.brokers.base import AssetClass

_PLANS_DIR = Path(__file__).resolve().parents[4] / ".fux" / "rules"
_YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)


@dataclass
class Plan:
    plan_id: str
    horizon: str
    targets: dict[AssetClass, float]
    bands: dict[str, float] = field(default_factory=dict)
    rules: list[str] = field(default_factory=list)

    def band_for(self, cls: AssetClass) -> float:
        """Drift tolerance (percentage points) for a class — its own, else default."""
        return self.bands.get(cls.value, self.bands.get("default", 5.0))


def _plan_path(plan_id: str) -> Path:
    return _PLANS_DIR / f"{plan_id}.plan.md"


def _parse_targets(raw: dict) -> dict[AssetClass, float]:
    targets: dict[AssetClass, float] = {}
    for key, pct in (raw.get("targets") or {}).items():
        targets[AssetClass(key)] = float(pct)
    total = round(sum(targets.values()), 2)
    if targets and total != 100.0:
        raise ValueError(f"plan targets must sum to 100, got {total}")
    return targets


def load_plan(plan_id: str = "core-allocation") -> Plan:
    """Parse `.fux/rules/<plan_id>.plan.md` → Plan. Raises if missing/malformed."""
    path = _plan_path(plan_id)
    if not path.exists():
        raise FileNotFoundError(f"no plan entry: {path}")
    match = _YAML_BLOCK.search(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"plan {plan_id}: no ```yaml targets block")
    raw = yaml.safe_load(match.group(1)) or {}
    return Plan(
        plan_id=raw.get("plan_id", plan_id),
        horizon=raw.get("horizon", "long-term"),
        targets=_parse_targets(raw),
        bands={str(k): float(v) for k, v in (raw.get("bands") or {}).items()},
        rules=list(raw.get("rules") or []),
    )


def plan_targets(plan_id: str = "core-allocation") -> dict[AssetClass, float]:
    """Convenience: just the AssetClass→pct map, for `HoldingsAggregator(targets=…)`."""
    return load_plan(plan_id).targets


def available_plans() -> list[str]:
    """Plan ids with a committed `.fux/rules/<id>.plan.md` entry."""
    return sorted(p.name.removesuffix(".plan.md") for p in _PLANS_DIR.glob("*.plan.md"))


__all__ = ["Plan", "available_plans", "load_plan", "plan_targets"]
