"""Position exit rules — first of (-20% guard, 20-day-low stop, end-of-hold) to fire.

`leg_exit` walks a held name's daily closes from entry and returns the bar index it exits on and
why: the -20% hard guard, a close below the prior 20-day low (when `stop_on`), or the scheduled
end of the holding window (the weekly-rebalance reselection). Pure; the caller turns the exit bar
into a net round-trip via `edge_costs`. Out-of-tranche exits are handled by the weekly rebalance
reselecting the sleeve, not here.
"""

from __future__ import annotations

from app.modules.edges.factor_schema import FactorConfig

GUARD_PCT = -20.0  # hard -20% drawdown guard on a single position
_STOP_LOOKBACK = 20


def twenty_day_low(closes: list[float], t: int, n: int = _STOP_LOOKBACK) -> float:
    """Lowest close over the prior n bars (excluding t); falls back to closes[t] early on."""
    window = closes[max(0, t - n) : t]
    return min(window) if window else closes[t]


def leg_exit(closes: list[float], t0: int, hold: int, cfg: FactorConfig) -> tuple[int, str]:
    """Bar index + reason this leg exits, entering at t0 and holding at most `hold` bars."""
    entry = closes[t0]
    end = min(t0 + hold, len(closes) - 1)
    for t in range(t0 + 1, end + 1):
        cur = closes[t]
        if entry > 0 and (cur / entry - 1.0) * 100 <= GUARD_PCT:
            return t, "guard_-20pct"
        if cfg.stop_on and cur < twenty_day_low(closes, t):
            return t, "20d_low_stop"
    return end, "rebalance"
