"""Hand-checked cost model for the edge engine — frictions + STCG + slippage.

The figure here is worked out by hand so a regression in any cost component is caught.
For qty=100, buy=100, sell=110, held 5 days (short-term):
  gross      = 100*(110-100)                       = 1000
  brokerage  = 2*20                                =   40
  stt        = 0.1%  * (100*100 + 100*110)         =   21
  friction   = 0.03% * 21000                       =    6.3
  stcg       = 20%   * 1000  (ST gain)             =  200
  after_tax  = 1000 - 40 - 21 - 6.3 - 200          =  732.7
  slippage   = 0.05% * 10000 + 0.05% * 11000       =   10.5
  net        = 732.7 - 10.5                         =  722.2
  net_pct    = 722.2 / 10000 * 100                  =    7.222 %

    uv run pytest tests/test_edge_costs.py -v
"""

from __future__ import annotations

from datetime import date

from app.modules.edges.edge_costs import net_pct
from app.modules.signals.strategy_config import CostsCfg

COSTS = CostsCfg()


def test_known_answer_net_pct_after_all_costs():
    r = net_pct(100, 110, 100.0, date(2024, 1, 1), date(2024, 1, 6), COSTS)
    assert round(r, 3) == 7.222  # exact hand-computed figure above


def test_slippage_lowers_the_net():
    args = (100, 110, 100.0, date(2024, 1, 1), date(2024, 1, 6), COSTS)
    assert net_pct(*args, slippage_pct=0.0) > net_pct(*args, slippage_pct=0.20)


def test_short_horizon_pays_stcg_long_horizon_does_not():
    short = net_pct(100, 110, 100.0, date(2024, 1, 1), date(2024, 1, 6), COSTS)
    long = net_pct(100, 110, 100.0, date(2022, 1, 1), date(2024, 1, 6), COSTS)
    assert long > short  # no 20% STCG on the > 12-month hold
