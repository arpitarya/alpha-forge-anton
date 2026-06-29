"""Deterministic position sizing — four constraints, the binding (smallest) one wins.

Pure math, no clock, no I/O, LLM-free (the determinism/$0 contract). Each method bounds the
position for a different reason; the recommendation is the **most conservative** bound, so
no single assumption can over-size. Output is SHOWN to the human for approval, never applied
and never an order. Mirrors `make-a-plan`: fixed-risk + downside + liquidity + Kelly.
"""

from __future__ import annotations

from app.modules.flow.flow_sizing_schema import SizingConstraint, SizingInputs, SizingResult


def _fixed_risk(i: SizingInputs) -> SizingConstraint:
    # Risk a fixed fraction of capital: a stop-out (stop_pct move) loses risk_pct of capital.
    notional = i.capital * (i.risk_pct / 100) / (i.stop_pct / 100) if i.stop_pct else 0.0
    return SizingConstraint(
        name="fixed-risk",
        notional=notional,
        note=f"{i.risk_pct:.1f}% of capital at a {i.stop_pct:.0f}% stop",
    )


def _downside_cap(i: SizingInputs) -> SizingConstraint:
    # Cap so a catastrophic guard_pct move loses at most max_loss_pct of capital (drawdown guard).
    notional = i.capital * (i.max_loss_pct / 100) / (i.guard_pct / 100) if i.guard_pct else 0.0
    return SizingConstraint(
        name="downside-cap",
        notional=notional,
        note=f"≤{i.max_loss_pct:.0f}% loss if the {i.guard_pct:.0f}% guard breaches",
    )


def _adv_cap(i: SizingInputs) -> SizingConstraint:
    # Stay a small share of a day's liquidity so exit doesn't move the price. 0 ADV → not binding.
    notional = i.adv_inr * (i.participation_pct / 100) if i.adv_inr > 0 else float("inf")
    note = (
        f"≤{i.participation_pct:.0f}% of ADV" if i.adv_inr > 0 else "no ADV supplied — not applied"
    )
    return SizingConstraint(name="adv-cap", notional=notional, note=note)


def _kelly(i: SizingInputs) -> SizingConstraint:
    # Fractional Kelly: full f* = p - (1-p)/b, then take only kelly_fraction of it (de-risked).
    full = i.win_prob - (1 - i.win_prob) / i.payoff_ratio if i.payoff_ratio else 0.0
    f = max(0.0, full) * i.kelly_fraction
    return SizingConstraint(
        name="fractional-kelly",
        notional=i.capital * f,
        note=f"{i.kelly_fraction:.2f}x Kelly (p={i.win_prob:.2f}, b={i.payoff_ratio:.1f})",
    )


def size(i: SizingInputs) -> SizingResult:
    """Compute the four bounds; recommend the binding minimum — deterministic, shown not applied."""
    constraints = [_fixed_risk(i), _downside_cap(i), _adv_cap(i), _kelly(i)]
    binding = min(constraints, key=lambda c: c.notional)
    rec = max(
        0.0, min(binding.notional, i.capital)
    )  # clamp to [0, capital]; never short or over-lever
    pct = (rec / i.capital * 100) if i.capital else 0.0
    return SizingResult(
        constraints=[c for c in constraints if c.notional != float("inf")],
        binding=binding.name,
        recommended_notional=round(rec, 2),
        recommended_pct=round(pct, 2),
        notes=[
            f"binding constraint: {binding.name} — the most conservative bound wins",
            "shown for approval — never auto-applied, never an order",
        ],
    )
