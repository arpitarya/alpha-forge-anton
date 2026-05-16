"""Zerodha Kite equity, ETF, and COIN MF holdings — BrokerSource impl."""

from __future__ import annotations

import os
from datetime import UTC, datetime

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import clear_session
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
    WalletBalance,
)
from app.modules.brokers.zerodha.zerodha_dump import (
    is_csv_fresh,
    live_csv_path,
    read_csv,
    write_csv,
)
from app.modules.brokers.zerodha.zerodha_instruments import (
    name_lookup,
    name_lookup_sync,
    type_lookup,
    type_lookup_sync,
)
from app.modules.brokers.zerodha.zerodha_source_helper import (
    REQUIRED_ENV,
    acquire_enctoken,
    env,
    fetch_holdings_json,
    fetch_margins_json,
    fetch_mf_holdings_json,
)

logger = get_logger("brokers.zerodha_kite")

__all__ = ["REQUIRED_ENV", "ZerodhaKiteSource", "acquire_enctoken", "env"]


def _asset_class(itype: str) -> AssetClass:
    return AssetClass.ETF if itype.upper() == "ETF" else AssetClass.EQUITY


def _holding_from_row(
    r: dict, slug: str, names: dict[str, str] | None = None, types: dict[str, str] | None = None
) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    invested, current = qty * avg, qty * ltp
    pnl = current - invested
    symbol = str(r.get("tradingsymbol") or "").upper()
    itype = (types or {}).get(symbol, "EQ")
    # Kite returns `day_change_percentage` for equity rows; falls back to 0.
    day_pct = float(r.get("day_change_percentage") or r.get("day_change_pct") or 0)
    return Holding(
        source=slug, asset_class=_asset_class(itype),
        symbol=symbol, name=(r.get("name") or (names or {}).get(symbol)) or None,
        isin=r.get("isin"), quantity=qty, avg_price=avg, last_price=ltp,
        invested=invested, current_value=current, pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
        day_change_pct=day_pct,
        exchange=r.get("exchange"),
    )


def _holding_from_csv(
    r: dict[str, str], slug: str, names: dict[str, str] | None = None,
    types: dict[str, str] | None = None,
) -> Holding:
    g = r.get
    symbol = str(g("tradingsymbol") or "").upper()
    name = g("name") or (names or {}).get(symbol)
    ac_str = g("asset_class") or ""
    itype = (types or {}).get(symbol, "EQ")
    try:
        asset_class = AssetClass(ac_str) if ac_str else _asset_class(itype)
    except ValueError:
        asset_class = AssetClass.EQUITY
    return Holding(
        source=slug, asset_class=asset_class,
        symbol=symbol, name=name or None, isin=g("isin") or None,
        quantity=float(g("quantity") or 0), avg_price=float(g("average_price") or 0),
        last_price=float(g("last_price") or 0), invested=float(g("invested") or 0),
        current_value=float(g("current_value") or 0), pnl=float(g("pnl") or 0),
        pnl_pct=float(g("pnl_pct") or 0),
        day_change_pct=float(g("day_change_pct") or 0),
        exchange=g("exchange") or None,
    )


def _mf_holding_from_row(r: dict, slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    invested, current = qty * avg, qty * ltp
    pnl = float(r.get("pnl") or current - invested)
    sym = str(r.get("tradingsymbol") or "").upper()
    return Holding(
        source=slug, asset_class=AssetClass.MUTUAL_FUND,
        symbol=sym, name=r.get("fund") or None, isin=sym or None,
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=invested, current_value=current, pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
    )


class ZerodhaKiteSource(BrokerSource):
    slug = "zerodha"
    label = "Zerodha (Kite)"
    kind = SourceKind.API
    supports_cash = True
    notes = (
        "Manual login: log in to kite.zerodha.com inside the AlphaForge "
        "Chrome (started with --remote-debugging-port=9299). AlphaForge never "
        "stores your password or TOTP. Set ZERODHA_USER_ID in .env.cred.local."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY
        self.refetch_seconds = int(os.getenv("ZERODHA_REFETCH_SECONDS", "3600"))

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            names, types = name_lookup_sync(), type_lookup_sync()
            logger.info("Zerodha Kite: %d holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug, names, types) for r in rows]
        try:
            enctoken = await acquire_enctoken()
            rows = await fetch_holdings_json(enctoken)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (401, 403):
                logger.warning(
                    "Zerodha: auth rejected (%s) — clearing session, re-logging via Chrome CDP. "
                    "Ensure kite.zerodha.com is open and logged in.",
                    status,
                )
                clear_session("zerodha")
                enctoken = await acquire_enctoken(force=True)
                rows = await fetch_holdings_json(enctoken)
            else:
                raise
        names = await name_lookup()
        types = await type_lookup()
        for r in rows:
            sym = str(r.get("tradingsymbol") or "").upper()
            if not r.get("name"):
                r["name"] = names.get(sym, "")
            r["asset_class"] = _asset_class(types.get(sym, "EQ")).value
        try:
            mf_rows = await fetch_mf_holdings_json(enctoken)
            for r in mf_rows:
                r["name"] = r.get("fund", "")
                r["asset_class"] = AssetClass.MUTUAL_FUND.value
        except Exception as e:
            logger.warning("Zerodha COIN: MF holdings unavailable (%s) — skipping", e)
            mf_rows = []
        write_csv(rows + mf_rows, live_csv_path())
        eq_etf = [_holding_from_row(r, self.slug, names, types) for r in rows]
        mf = [_mf_holding_from_row(r, self.slug) for r in mf_rows]
        out = eq_etf + mf
        logger.info(
            "Zerodha Kite: %d equity/ETF + %d COIN MF → cached to CSV", len(eq_etf), len(mf)
        )
        return out

    async def fetch_cash(self) -> WalletBalance:
        enctoken = await acquire_enctoken()
        try:
            data = await fetch_margins_json(enctoken)
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code in (401, 403):
                clear_session("zerodha")
                enctoken = await acquire_enctoken(force=True)
                data = await fetch_margins_json(enctoken)
            else:
                raise
        equity = data.get("equity") or {}
        cash = float((equity.get("available") or {}).get("cash") or 0.0)
        return WalletBalance(
            source=self.slug, currency="INR", cash=round(cash, 2),
            as_of=datetime.now(UTC),
        )
