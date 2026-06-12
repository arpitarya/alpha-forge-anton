"""Private holdings disclosure + provider floor for Orff.

The chokepoint that lets Orff answer holdings questions without leaking. Two guarantees,
matching the user's choices (percentages-only disclosure + trusted-provider-only routing):

1. `disclosed_context()` emits ONLY percentages / points / counts — never ₹ or symbols
   (safe by construction; independently verified by `probes/holdings_disclosure_probe.py`).
2. `enforce_floor()` pins any private (holdings-bearing) query to a trusted provider from
   the registry manifest, so even the redacted aggregate never reaches a free third party.

See the Fux `secure-holdings-plan` entry.
"""

from __future__ import annotations

from alphaforge_anton_llm import registry
from alphaforge_anton_llm.types import QueryType

from app.modules.plans.plan_drift import drift_for_plan, has_live_data

# Returned by enforce_floor: (query_type, preferred_provider, confirmed, user_notice).
Floor = tuple[QueryType, str | None, bool, str | None]


def disclosed_context(plan_id: str = "core-allocation") -> str:
    """A percentages-only holdings block safe to place in any prompt."""
    plan, rows = drift_for_plan(plan_id)
    if not has_live_data(rows):
        return (
            "Holdings context: no live broker data is cached right now, so allocation "
            "percentages are unavailable. Tell the user that plainly. Do NOT invent figures "
            "and do NOT show a sample/demo/illustrative holdings table — fabricated rows in "
            "a finance terminal read as real data. Instead, point the user to the broker "
            "sources panel to sync a broker (the CDP Chrome tab must be logged in) or to "
            "upload a holdings CSV, then continue the conversation."
        )
    lines = [
        f"- {r.asset_class}: target {r.target_pct:.0f}%, actual {r.actual_pct:.0f}%, "
        f"drift {r.drift_pct:+.0f}pts ({r.status})" + (f" — {r.action}" if r.action else "")
        for r in rows
    ]
    head = (
        f"Disclosed holdings context for plan '{plan.plan_id}' — PERCENTAGES ONLY (no "
        "amounts, no symbols). Advise using these figures; never ask for or infer ₹ values "
        "unless the user explicitly requests amounts."
    )
    return head + "\n" + "\n".join(lines)


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


__all__ = ["Floor", "disclosed_context", "enforce_floor"]
