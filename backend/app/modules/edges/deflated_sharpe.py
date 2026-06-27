"""Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014) — is the Sharpe real after N trials?

The headline Sharpe is inflated by (a) having tried N configs and (b) non-normal returns. DSR is
the probability the true Sharpe is > 0 after deflating by the expected maximum Sharpe under the
null of N trials and adjusting for skew/kurtosis. N is the *declared trial budget* (read from the
trial-ledger), not a number we pick after the fact — that is the integrity the funnel enforces.
Pure; uses `statistics.NormalDist` for the normal CDF / inverse-CDF.
"""

from __future__ import annotations

import math
from statistics import NormalDist, fmean, variance

_GAMMA = 0.5772156649015329  # Euler-Mascheroni
_N = NormalDist()


def _moments(xs: list[float]) -> tuple[float, float, float, float]:
    n = len(xs)
    m = fmean(xs)
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    if sd == 0:
        return m, 0.0, 0.0, 3.0
    skew = sum(((x - m) / sd) ** 3 for x in xs) / n
    kurt = sum(((x - m) / sd) ** 4 for x in xs) / n
    return m, sd, skew, kurt


def sharpe(xs: list[float]) -> float:
    m, sd, _, _ = _moments(xs)
    return m / sd if sd > 0 else 0.0


def expected_max_sharpe(var_sr: float, n_trials: int) -> float:
    """E[max Sharpe] under the null of n_trials independent strategies (the deflation bar)."""
    if n_trials < 2 or var_sr <= 0:
        return 0.0
    a = _N.inv_cdf(1 - 1 / n_trials)
    b = _N.inv_cdf(1 - 1 / (n_trials * math.e))
    return math.sqrt(var_sr) * ((1 - _GAMMA) * a + _GAMMA * b)


def deflated_sharpe(returns: list[float], trial_sharpes: list[float], n_trials: int) -> float:
    """Probability the Sharpe is genuinely positive after N-trial + non-normality deflation."""
    n_obs = len(returns)
    if n_obs < 2:
        return 0.0
    _, _, skew, kurt = _moments(returns)
    sr = sharpe(returns)
    var_sr = variance(trial_sharpes) if len(trial_sharpes) > 1 else 0.0
    sr0 = expected_max_sharpe(var_sr, n_trials)
    denom = math.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4 * sr * sr))
    return round(_N.cdf((sr - sr0) * math.sqrt(n_obs - 1) / denom), 4)
