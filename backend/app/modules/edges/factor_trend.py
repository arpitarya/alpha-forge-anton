"""Dual-momentum trend filter — only deploy when NIFTY ≥ its 200-DMA, else cash.

Absolute-momentum overlay on the cross-sectional (relative-momentum) sleeve: a strong stock in
a falling market still falls. When the index is below its 200-day average — or there isn't yet
200 days of history to judge — the sleeve goes to cash (honest: we don't deploy on an unconfirmed
trend). Pure: a simple trailing mean, no ta-lib, no clock.
"""

from __future__ import annotations

_DMA = 200


def sma(series: list[float], t: int, n: int = _DMA) -> float | None:
    """Simple moving average of the last n values ending at t; None if history < n."""
    if t + 1 < n:
        return None
    return sum(series[t - n + 1 : t + 1]) / n


def nifty_above_200dma(nifty: list[float], t: int) -> bool:
    """True only when the index close at t is at or above its 200-DMA (else cash)."""
    avg = sma(nifty, t)
    return avg is not None and nifty[t] >= avg
