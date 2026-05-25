"""INDmoney holdings — BrokerSource impl over CDP browser fetch + on-disk cache.

Auth flow: user logs in to indmoney.com inside the AlphaForge Anton Chrome instance
started with --remote-debugging-port=9299. `fetch()` attaches over CDP, navigates
to the US stocks portfolio page, intercepts the holdings XHR, and caches to disk.
Subsequent `fetch()` calls within INDMONEY_REFETCH_SECONDS return from cache.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

from app.core.logging import get_logger
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
    WalletBalance,
)
from app.modules.brokers.indmoney.indmoney_cash_helper import capture_indmoney_cash
from app.modules.brokers.indmoney.indmoney_dump import (
    is_csv_fresh,
    live_csv_path,
    read_csv,
    write_csv,
)
from app.modules.brokers.broker_env import source_ready
from app.modules.brokers.indmoney.indmoney_source_helper import (
    REQUIRED_ENV,
    env,
    fetch_holdings_via_browser,
)

logger = get_logger("brokers.indmoney")

__all__ = ["REQUIRED_ENV", "IndMoneySource", "env"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    # Use API-provided pre-computed values; fall back to qty*price math.
    inv = float(r.get("invested") or 0) or qty * avg
    cur = float(r.get("current_value") or 0) or qty * ltp
    pnl = float(r.get("pnl") or 0) or cur - inv
    pnl_pct = float(r.get("pnl_pct") or 0) or ((pnl / inv * 100) if inv else 0.0)
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        name=r.get("name") or None,
        isin=r.get("isin") or None,
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=inv, current_value=cur, pnl=pnl,
        pnl_pct=pnl_pct,
        day_change_pct=float(r.get("day_change_pct") or 0.0),
        currency="USD",
        exchange=r.get("exchange") or "NYSE",
        sector=r.get("sector") or None,
    )


class IndMoneySource(BrokerSource):
    slug = "indmoney"
    label = "INDmoney"
    kind = SourceKind.API
    supports_cash = True
    currency = "USD"
    notes = (
        "Manual login: log in to indmoney.com inside the AlphaForge Anton Chrome "
        "(started with --remote-debugging-port=9299). AlphaForge Anton never stores "
        "your password or OTP. Set INDMONEY_USER_ID in .env.cred.local."
    )

    def __init__(self) -> None:
        super().__init__()
        if source_ready(REQUIRED_ENV, env):
            self._status = SourceStatus.READY
        self.refetch_seconds = int(os.getenv("INDMONEY_REFETCH_SECONDS", "3600"))

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("INDmoney: %d holdings from on-disk cache", len(rows))
            return [_holding_from_row(r, self.slug) for r in rows]
        try:
            rows = await fetch_holdings_via_browser()
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ("401", "403", "login", "expired")):
                logger.warning("INDmoney: fetch failed (%s) — retrying with forced login", e)
                rows = await fetch_holdings_via_browser(force_login=True)
            else:
                raise
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("INDmoney: fetched %d holdings → cached to disk", len(out))
        return out

    async def fetch_cash(self) -> WalletBalance:
        cash = await capture_indmoney_cash()
        return WalletBalance(
            source=self.slug, currency="USD", cash=round(cash, 2),
            as_of=datetime.now(UTC), available=True,
        )
