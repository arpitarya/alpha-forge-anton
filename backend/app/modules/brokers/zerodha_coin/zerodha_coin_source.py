"""Zerodha Coin — mutual fund holdings BrokerSource."""

from __future__ import annotations

import os

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import clear_session
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind, SourceStatus
from app.modules.brokers.zerodha_coin.zerodha_coin_dump import (
    is_csv_fresh,
    live_csv_path,
    read_csv,
    write_csv,
)
from app.modules.brokers.zerodha_coin.zerodha_coin_source_helper import (
    REQUIRED_ENV,
    acquire_token,
    env,
    fetch_holdings_json,
)

logger = get_logger("brokers.zerodha_coin")

__all__ = ["REQUIRED_ENV", "ZerodhaCoinSource"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    invested, current = qty * avg, qty * ltp
    pnl = float(r.get("pnl") or current - invested)
    sym = str(r.get("tradingsymbol") or "").upper()
    return Holding(
        source=slug, asset_class=AssetClass.MUTUAL_FUND,
        symbol=sym, name=r.get("fund") or r.get("name") or None,
        isin=sym or None,
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=invested, current_value=current, pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
    )


def _holding_from_csv(r: dict[str, str], slug: str) -> Holding:
    g = r.get
    invested = float(g("invested") or 0)
    pnl = float(g("pnl") or 0)
    return Holding(
        source=slug, asset_class=AssetClass.MUTUAL_FUND,
        symbol=str(g("tradingsymbol") or "").upper(),
        name=g("name") or None,
        isin=g("isin") or None,
        quantity=float(g("quantity") or 0),
        avg_price=float(g("average_price") or 0),
        last_price=float(g("last_price") or 0),
        invested=invested,
        current_value=float(g("current_value") or 0),
        pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else float(g("pnl_pct") or 0),
    )


class ZerodhaCoinSource(BrokerSource):
    slug = "zerodha_coin"
    label = "Zerodha (Coin)"
    kind = SourceKind.API
    notes = (
        "Log in to kite.zerodha.com inside the AlphaForge Anton Chrome "
        "(--remote-debugging-port=9299). Set ZERODHA_USER_ID in .env.cred.local. "
        "Coin MF holdings are fetched via the same enctoken as Kite."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY
        self.refetch_seconds = int(os.getenv("ZERODHA_COIN_REFETCH_SECONDS", "3600"))

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("Zerodha Coin: %d MF holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug) for r in rows]
        try:
            token = await acquire_token()
            rows = await fetch_holdings_json(token)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (401, 403):
                logger.warning("Zerodha Coin: auth rejected (%s) — forcing re-login", status)
                clear_session("zerodha_coin")
                token = await acquire_token(force=True)
                rows = await fetch_holdings_json(token)
            else:
                raise
        for r in rows:
            r.setdefault("name", r.get("fund", ""))
            r.setdefault("asset_class", "mutual_fund")
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("Zerodha Coin: fetched %d MF holdings → cached to CSV", len(out))
        return out
