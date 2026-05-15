"""Angel One holdings — BrokerSource impl over SmartAPI + CSV cache.

Free SmartAPI app + TOTP: register at smartapi.angelbroking.com, enable TOTP
on the account, set ANGELONE_API_KEY / CLIENT_ID / MPIN / TOTP_SECRET in
.env.cred.local. The 6-digit code is derived locally each login.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import IO

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import clear_session
from app.modules.brokers.angelone.angelone_dump import (
    is_csv_fresh,
    live_csv_path,
    read_csv,
    write_csv,
)
from app.modules.brokers.angelone.angelone_source_helper import (
    REQUIRED_ENV,
    acquire_token,
    env,
    fetch_holdings_json,
    fetch_rms_json,
)
from app.modules.brokers.angelone.csv import AngelOneCSVSource as _AngelOneCSV
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
    WalletBalance,
)

logger = get_logger("brokers.angelone")

__all__ = ["REQUIRED_ENV", "AngelOneSource", "acquire_token", "env"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    # SmartAPI uses lowercase keys without underscores (averageprice, ltp).
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("averageprice") or r.get("average_price") or 0)
    ltp = float(r.get("ltp") or r.get("last_price") or r.get("close") or 0)
    inv, cur = qty * avg, qty * ltp
    pnl = cur - inv
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        isin=r.get("isin") or None,
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=inv, current_value=cur, pnl=pnl,
        pnl_pct=(pnl / inv * 100) if inv else 0.0,
        exchange=r.get("exchange") or "NSE",
    )


def _holding_from_csv(r: dict[str, str], slug: str) -> Holding:
    g = r.get
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(g("tradingsymbol") or "").upper(),
        name=g("name") or None, isin=g("isin") or None,
        quantity=float(g("quantity") or 0), avg_price=float(g("average_price") or 0),
        last_price=float(g("last_price") or 0), invested=float(g("invested") or 0),
        current_value=float(g("current_value") or 0), pnl=float(g("pnl") or 0),
        pnl_pct=float(g("pnl_pct") or 0), exchange=g("exchange") or None,
    )


class AngelOneSource(BrokerSource):
    slug = "angelone"
    label = "Angel One (SmartAPI)"
    kind = SourceKind.API
    supports_cash = True
    notes = (
        "Register a free app at smartapi.angelbroking.com, enable TOTP, then "
        "set ANGELONE_API_KEY / CLIENT_ID / MPIN / TOTP_SECRET in "
        ".env.cred.local. AlphaForge derives the TOTP locally."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        holdings = _AngelOneCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("Angel One: %d holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug) for r in rows]
        try:
            token = await acquire_token()
            rows = await fetch_holdings_json(token)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (401, 403):
                logger.warning("Angel One: auth rejected (%s) — forcing re-login", status)
                clear_session("angelone")
                token = await acquire_token(force=True)
                rows = await fetch_holdings_json(token)
            else:
                raise
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("Angel One: fetched %d holdings → cached to CSV", len(out))
        return out

    async def fetch_cash(self) -> WalletBalance:
        token = await acquire_token()
        try:
            data = await fetch_rms_json(token)
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code in (401, 403):
                clear_session("angelone")
                token = await acquire_token(force=True)
                data = await fetch_rms_json(token)
            else:
                raise
        cash = float(
            data.get("availablecash") or data.get("net") or data.get("availablelimitmargin") or 0.0
        )
        return WalletBalance(
            source=self.slug, currency="INR", cash=round(cash, 2),
            as_of=datetime.now(UTC),
        )
