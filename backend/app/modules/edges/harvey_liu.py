"""Harvey-Liu multiple-testing haircut — shrink the Sharpe's t-stat for N tests.

Harvey & Liu (2015): a Sharpe found after testing N strategies needs a higher bar. We convert the
Sharpe to its t-statistic, inflate its p-value for N tests (Bonferroni — deliberately conservative,
the honest direction for a discovery funnel), and read back the haircut t-stat and the % of Sharpe
lost. `haircut_t` is the multiple-testing-adjusted t-stat reported on the TestReport. Pure.
(BHY / Holm step-downs are a less-conservative refinement noted for a later slice.)
"""

from __future__ import annotations

import math
from statistics import NormalDist

_N = NormalDist()


def haircut(sharpe: float, n_obs: int, n_tests: int) -> tuple[float, float]:
    """(haircut_t, haircut_fraction). fraction = share of the Sharpe lost to the N tests."""
    if n_obs < 2 or sharpe <= 0:
        return 0.0, 1.0
    t = sharpe * math.sqrt(n_obs)
    p = 2 * (1 - _N.cdf(abs(t)))  # two-sided single-test p-value
    p_adj = min(1.0, p * max(1, n_tests))  # Bonferroni inflation (non-linear in N)
    if p_adj >= 1.0:
        return 0.0, 1.0
    t_adj = _N.inv_cdf(1 - p_adj / 2)
    sr_adj = t_adj / math.sqrt(n_obs)
    return round(t_adj, 4), round(max(0.0, 1 - sr_adj / sharpe), 4)
