"""Binance spot-wallet holdings — BrokerSource over CDP browser fetch (USD/USDT)."""

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
from app.modules.brokers.binance.binance_cash_helper import capture_binance_cash
from app.modules.brokers.binance.binance_dump import (
    is_csv_fresh,
    live_csv_path,
    read_csv,
    write_csv,
)
from app.modules.brokers.binance.binance_source_helper import (
    REQUIRED_ENV,
    env,
    fetch_holdings_via_browser,
)

logger = get_logger("brokers.binance")

__all__ = ["REQUIRED_ENV", "BinanceSource", "env"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    inv = float(r.get("invested") or 0) or qty * avg
    cur = float(r.get("current_value") or 0) or qty * ltp
    pnl = float(r.get("pnl") or 0) or cur - inv
    pnl_pct = float(r.get("pnl_pct") or 0) or ((pnl / inv * 100) if inv else 0.0)
    return Holding(
        source=slug, asset_class=AssetClass.CRYPTO,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        name=r.get("name") or None,
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=inv, current_value=cur, pnl=pnl, pnl_pct=pnl_pct,
        currency="USD",
        exchange=r.get("exchange") or "BINANCE",
        sector=r.get("sector") or "Crypto",
    )


class BinanceSource(BrokerSource):
    slug = "binance"
    label = "Binance"
    kind = SourceKind.API
    supports_cash = True
    currency = "USD"
    notes = (
        "Manual login: log in to binance.com inside the AlphaForge Anton Chrome "
        "(started with --remote-debugging-port=9299). AlphaForge Anton never stores "
        "your password or 2FA code. Set BINANCE_USER_ID in .env.cred.local."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY
        self.refetch_seconds = int(os.getenv("BINANCE_REFETCH_SECONDS", "3600"))

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("Binance: %d holdings from on-disk cache", len(rows))
            return [_holding_from_row(r, self.slug) for r in rows]
        try:
            rows = await fetch_holdings_via_browser()
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ("401", "403", "login", "expired")):
                logger.warning("Binance: fetch failed (%s) — retrying with forced login", e)
                rows = await fetch_holdings_via_browser(force_login=True)
            else:
                raise
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("Binance: fetched %d holdings → cached to disk", len(out))
        return out

    async def fetch_cash(self) -> WalletBalance:
        cash = await capture_binance_cash()
        return WalletBalance(
            source=self.slug, currency="USD", cash=round(cash, 2),
            as_of=datetime.now(UTC), available=True,
        )
