"""CSCV -> PBO: the probability the in-sample-best config is overfit (Bailey & Lopez de Prado).

Combinatorially-Symmetric Cross-Validation splits the return timeline into S even partitions and,
over every way to choose S/2 as in-sample, picks the config with the best in-sample Sharpe and
measures its out-of-sample rank. PBO = the fraction of splits where that "best" config lands below
the OOS median (logit < 0). High PBO ⇒ selecting the top backtest is no better than a coin flip:
the canonical overfitting test the funnel runs over the 24-config trial grid. Pure, deterministic.
"""

from __future__ import annotations

import math
from itertools import combinations


def _sharpe(xs: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m / sd if sd > 0 else 0.0


def _partitions(n_obs: int, n_parts: int) -> list[list[int]]:
    step = n_obs // n_parts
    return [list(range(k * step, (k + 1) * step)) for k in range(n_parts)]


def pbo(matrix: list[list[float]], n_partitions: int = 16) -> float:
    """matrix = one return series per config (aligned). Returns PBO in [0, 1]."""
    n_cfg = len(matrix)
    if n_cfg < 2:
        return 0.0
    n_obs = min(len(r) for r in matrix)
    n_parts = min(n_partitions - (n_partitions % 2), (n_obs // 2) * 2)  # even and <= n_obs
    if n_parts < 2:
        return 0.0
    parts = _partitions(n_obs, n_parts)
    half = n_parts // 2
    below = total = 0
    for combo in combinations(range(n_parts), half):
        is_rows = [i for p in combo for i in parts[p]]
        oos_rows = [i for p in range(n_parts) if p not in combo for i in parts[p]]
        is_sr = [_sharpe([matrix[c][i] for i in is_rows]) for c in range(n_cfg)]
        best = max(range(n_cfg), key=lambda c: is_sr[c])
        oos_sr = [_sharpe([matrix[c][i] for i in oos_rows]) for c in range(n_cfg)]
        rank = 1 + sum(1 for c in range(n_cfg) if oos_sr[c] < oos_sr[best])
        omega = rank / (n_cfg + 1)  # in (0, 1) since rank in [1, n_cfg]
        total += 1
        if math.log(omega / (1 - omega)) < 0:
            below += 1
    return round(below / total, 4) if total else 0.0
