"""Orchestrate a deterministic `ActionPlan` over current holdings.

holdings → per-symbol quotes (`quote_source`) → `indicators` → `signal_rules` →
sorted `ActionPlan`. Holdings + quote function are injectable so the probe and
tests run offline; verdicts are sorted so the same inputs serialise byte-identically.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.brokers.broker_schemas import AssetClass, Holding
from app.modules.brokers.fx import to_inr
from app.modules.signals import plan_diff, plan_store
from app.modules.signals.indicators import compute
from app.modules.signals.quote_source import OHLCV, daily_ohlcv
from app.modules.signals.signal_rules import HoldingFacts, evaluate
from app.modules.signals.signal_schema import ActionPlan, PlanDiff
from app.modules.signals.strategy_config import StrategyConfig, load_config

QuoteFn = Callable[[str, str | None], Awaitable[OHLCV | None]]


def _is_swing(h: Holding) -> bool:
    """INR-listed equity only — US (IndMoney) and crypto are out of scope (§5)."""
    return h.asset_class == AssetClass.EQUITY and h.currency == "INR"


def _equity_book(holdings: list[Holding]) -> float:
    return sum(to_inr(h.current_value, h.currency) for h in holdings if _is_swing(h))


async def build_action_plan(
    cfg: StrategyConfig | None = None,
    holdings: list[Holding] | None = None,
    quote: QuoteFn = daily_ohlcv,
) -> ActionPlan:
    cfg = cfg or load_config()
    holdings = HoldingsAggregator().all_holdings() if holdings is None else holdings
    book = _equity_book(holdings) or 1.0

    verdicts = []
    for h in holdings:
        covered = _is_swing(h)
        weight = to_inr(h.current_value, h.currency) / book * 100 if covered else 0.0
        facts = HoldingFacts(
            symbol=h.symbol,
            avg_price=h.avg_price,
            pnl_pct=h.pnl_pct,
            weight_pct=round(weight, 2),
            covered=covered,
        )
        ind = compute(o) if covered and (o := await quote(h.symbol, h.exchange)) else None
        verdicts.append(evaluate(facts, ind, cfg))

    verdicts.sort(key=lambda v: (v.symbol, v.action.value))
    return ActionPlan(verdicts=verdicts, config_hash=cfg.hash(), universe_mode=cfg.universe.mode)


async def build_review(
    cfg: StrategyConfig | None = None,
    holdings: list[Holding] | None = None,
    quote: QuoteFn = daily_ohlcv,
) -> tuple[ActionPlan, PlanDiff]:
    """Today's ActionPlan + the diff vs the last saved plan (§7). Diff is best-effort."""
    hold = HoldingsAggregator().all_holdings() if holdings is None else holdings
    plan = await build_action_plan(cfg=cfg, holdings=hold, quote=quote)
    return plan, plan_diff.diff(hold, await plan_store.latest())
