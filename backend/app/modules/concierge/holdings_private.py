"""Private holdings disclosure + provider floor for Orff.

The chokepoint that lets Orff answer holdings questions without leaking. Guarantees:

1. `enforce_floor()` pins any private (holdings-bearing) query to a trusted provider from
   the registry manifest — a free third party never sees a private query.
2. `detailed_context()` discloses full holding rows ONLY when the resolved provider is
   trusted; anything else gets `disclosed_context()` — percentages / points / counts,
   never ₹ or symbols (independently verified by `probes/holdings_disclosure_probe.py`).

See the Fux `secure-holdings-plan` entry.
"""

from __future__ import annotations

from alphaforge_anton_llm import registry
from alphaforge_anton_llm.types import QueryType

from app.modules.concierge.holdings_detail import NO_LIVE_DATA, holdings_table, no_plan_context
from app.modules.plans.plan_drift import ClassDrift, drift_for_plan, has_live_data

# Returned by enforce_floor: (query_type, preferred_provider, confirmed, user_notice).
Floor = tuple[QueryType, str | None, bool, str | None]


def _drift_lines(rows: list[ClassDrift]) -> list[str]:
    return [
        f"- {r.asset_class}: target {r.target_pct:.0f}%, actual {r.actual_pct:.0f}%, "
        f"drift {r.drift_pct:+.0f}pts ({r.status})" + (f" — {r.action}" if r.action else "")
        for r in rows
    ]


def disclosed_context(plan_id: str = "core-allocation") -> str:
    """A percentages-only holdings block safe to place in any prompt."""
    try:
        plan, rows = drift_for_plan(plan_id)
    except (FileNotFoundError, ValueError):
        # Missing/malformed plan must never kill the chat stream — degrade to actuals.
        return no_plan_context(plan_id)
    if not has_live_data(rows):
        return NO_LIVE_DATA
    head = (
        f"Disclosed holdings context for plan '{plan.plan_id}' — PERCENTAGES ONLY (no "
        "amounts, no symbols). Advise using these figures; never ask for or infer ₹ values "
        "unless the user explicitly requests amounts."
    )
    return head + "\n" + "\n".join(_drift_lines(rows))


def detailed_context(provider: str | None, plan_id: str = "core-allocation") -> str:
    """Full holding rows for the trusted lane; percentages-only for anyone else.

    The chokepoint guard: callers pass the provider enforce_floor resolved — full
    detail is constructed only when that provider is in the trusted set.
    """
    if provider not in registry.trusted_providers():
        return disclosed_context(plan_id)
    table = holdings_table()
    if not table:
        return NO_LIVE_DATA
    try:
        plan, rows = drift_for_plan(plan_id)
        drift = (
            f"Drift vs plan '{plan.plan_id}':\n" + "\n".join(_drift_lines(rows))
            if has_live_data(rows) else ""
        )
    except (FileNotFoundError, ValueError):
        drift = (
            "No committed plan in the elgar store — drift and rebalancing advice are "
            "unavailable; suggest `elgar save plan/<id>` to unlock them."
        )
    head = (
        "Disclosed holdings context — FULL DETAIL, INR-normalised, authorized because "
        "this conversation is pinned to your trusted provider. Answer from these actual "
        "rows ONLY; never fabricate, extrapolate, or restate stale figures."
    )
    return head + "\n\n" + table + ("\n\n" + drift if drift else "")


def enforce_floor(provider: str, qt: QueryType) -> Floor:
    """Resolve routing for a query, forcing a trusted provider when it is private."""
    if not registry.is_private(qt):
        preferred = None if provider == "auto" else provider
        return qt, preferred, provider == "claude-sdk", None
    trusted = registry.trusted_providers()
    if provider in trusted:
        return qt, provider, True, None
    floor = sorted(trusted)[0] if trusted else None
    notice = (
        f"Holdings questions route only to your trusted provider "
        f"({floor or 'none configured'}) — the selected provider was overridden for privacy."
    )
    return qt, floor, True, notice


__all__ = ["Floor", "detailed_context", "disclosed_context", "enforce_floor"]
