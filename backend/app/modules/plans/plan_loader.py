"""Load a plan doc from the elgar store into typed rebalance targets.

Plans live in the **elgar store**, never in this public repo — Anton owns no store
path and reads them through the elgar API (`elgar_bridge`); elgar maintains the
store + path. Fux holds only `elgar://plan/<id>` links (see the `plan-store` Fux
entry). This reads the fenced ```yaml block of the `plans/<plan_id>` doc and maps it
onto `AssetClass`, so the plan drives `HoldingsAggregator.rebalance()` without
holdings ever leaving the machine. Read style (sync via the cached `get_sync`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import yaml

from app.modules.brokers.base import AssetClass
from app.modules.plans import elgar_bridge

_YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)
_COLLECTION = "plans"


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


def _parse_targets(raw: dict) -> dict[AssetClass, float]:
    targets: dict[AssetClass, float] = {}
    for key, pct in (raw.get("targets") or {}).items():
        targets[AssetClass(key)] = float(pct)
    total = round(sum(targets.values()), 2)
    if targets and total != 100.0:
        raise ValueError(f"plan targets must sum to 100, got {total}")
    return targets


def load_plan(plan_id: str = "core-allocation") -> Plan:
    """Parse the elgar `plans/<plan_id>` doc → Plan. Raises if missing/malformed."""
    text = elgar_bridge.get_sync(plan_id, collection=_COLLECTION)
    if not text:
        raise FileNotFoundError(f"no plan '{plan_id}' in elgar store (`elgar list --dir plans`)")
    match = _YAML_BLOCK.search(text)
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


async def available_plans() -> list[str]:
    """Plan ids present in the elgar store ([] when the store is absent)."""
    return sorted(d["id"] for d in await elgar_bridge.list_docs(collection=_COLLECTION))


__all__ = ["Plan", "available_plans", "load_plan", "plan_targets"]
