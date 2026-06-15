"""Orchestrate the screener: universe → quotes → indicators → ranked candidates.

Mirrors `review_service`: reuses `quote_source` + `indicators` (no duplication),
and takes injectable symbols + quote function so tests and the probe run offline
and deterministically.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.modules.signals.indicators import compute
from app.modules.signals.quote_source import OHLCV, daily_ohlcv
from app.modules.signals.screener_rules import rank, screen_one
from app.modules.signals.signal_schema import Candidate, ScreenResult
from app.modules.signals.strategy_config import StrategyConfig, load_config
from app.modules.signals.universe import resolve_universe

QuoteFn = Callable[[str, str | None], Awaitable[OHLCV | None]]


async def build_screen(
    cfg: StrategyConfig | None = None,
    theme: str | None = None,
    symbols: list[str] | None = None,
    quote: QuoteFn = daily_ohlcv,
    limit: int | None = None,
) -> ScreenResult:
    cfg = cfg or load_config()
    syms = resolve_universe(cfg, theme) if symbols is None else symbols

    candidates: list[Candidate] = []
    for symbol in syms:
        o = await quote(symbol, None)
        ind = compute(o) if o else None
        if ind is None:
            continue
        if (cand := screen_one(symbol, ind, cfg)) is not None:
            candidates.append(cand)

    top_n = limit or cfg.screener.top_n
    return ScreenResult(
        candidates=rank(candidates, top_n),
        config_hash=cfg.hash(),
        universe_mode=theme or cfg.universe.mode,
        universe_size=len(syms),
    )
