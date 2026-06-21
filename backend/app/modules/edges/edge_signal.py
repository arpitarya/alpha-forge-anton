"""Deterministic entry signals, keyed by id — pure functions, no LLM, no clock.

A signal is `(closes_up_to_i, i, params) -> bool`: does an entry fire at bar `i`?
`params` is a small tuple of ints the walk-forward gate optimises over a fixed grid
(≤2 knobs, by design). Two signals ship: `momentum` (real — close above an N-day
average) and `overfit_dayofmonth` (a deliberate trap — fires on one weekday index,
which fits in-sample noise and dies out-of-sample; it's the gate-2 acceptance case).
"""

from __future__ import annotations

from collections.abc import Callable

SignalFn = Callable[[list[float], int, tuple[int, ...]], bool]


def _momentum(closes: list[float], i: int, params: tuple[int, ...]) -> bool:
    """Fire when close > the trailing N-day average (N = params[0]). Real, robust."""
    n = params[0] if params else 20
    if i < n:
        return False
    window = closes[i - n : i]
    return closes[i] > sum(window) / n


def _overfit_dayofmonth(closes: list[float], i: int, params: tuple[int, ...]) -> bool:
    """Fire only on bar-index ≡ k (mod 7) — params[0]=k. Curve-fits noise, no real edge."""
    k = params[0] if params else 0
    return i % 7 == k


_REGISTRY: dict[str, SignalFn] = {
    "momentum": _momentum,
    "overfit_dayofmonth": _overfit_dayofmonth,
}

# Fixed param grid the walk-forward gate optimises over, per signal.
_GRID: dict[str, list[tuple[int, ...]]] = {
    "momentum": [(10,), (20,), (50,)],
    "overfit_dayofmonth": [(k,) for k in range(7)],
}


def get_signal(signal_id: str) -> SignalFn:
    if signal_id not in _REGISTRY:
        raise KeyError(f"unknown signal {signal_id!r}; known: {sorted(_REGISTRY)}")
    return _REGISTRY[signal_id]


def param_grid(signal_id: str) -> list[tuple[int, ...]]:
    return _GRID.get(signal_id, [()])
