"""The composable vocabulary — single source for what Orff may put in a UISpec.

Prompt, validator, and client whitelist must agree (`ui-component-contract`). The
fux registry knows *every* component in the repo; this narrows it to the curated
solar-ui primitives that are safe and meaningful to compose. The frontend
`compose.registry.ts` WHITELIST must mirror COMPOSABLE_COMPONENTS — guarded by
`just probe compose-registry`.
"""

from __future__ import annotations

from typing import Any

# Presentational solar-ui primitives with JSON-serializable props only.
COMPOSABLE_COMPONENTS: frozenset[str] = frozenset({
    "AllocationBar", "Badge", "Card", "Chip", "CountUp", "DataTable", "DeltaText",
    "DiffTable", "Divider", "DonutChart", "Icon", "Kbd", "LineChart", "LiveDot",
    "ProgressBar", "RiskBars", "Sparkline", "Stat", "StatGrid", "Text",
})

# Parameterless data hooks the client host resolves (`SpecHost.tsx`).
COMPOSABLE_HOOKS: frozenset[str] = frozenset({
    "useHoldings", "useTreemap", "usePlan", "usePlanDrift", "useProjection",
})


def narrow_registry(reg: dict) -> dict:
    """Filter a fux registry payload down to the composable vocabulary."""
    return {
        "components": [c for c in reg.get("components", [])
                       if c["name"] in COMPOSABLE_COMPONENTS],
        "hooks": [h for h in reg.get("hooks", []) if h["name"] in COMPOSABLE_HOOKS],
    }


def composable_errors(spec: dict[str, Any]) -> list[str]:
    """Walk a UISpec; report any component/hook outside the composable vocabulary."""
    errors: list[str] = []

    def walk(node: Any) -> None:
        if not isinstance(node, dict) or "text" in node:
            return
        name = node.get("component")
        if name and name not in COMPOSABLE_COMPONENTS:
            errors.append(f"component not composable: {name}")
        hook = node.get("data")
        if hook and hook not in COMPOSABLE_HOOKS:
            errors.append(f"data hook not composable: {hook}")
        for child in node.get("children") or []:
            walk(child)

    walk(spec)
    return errors
