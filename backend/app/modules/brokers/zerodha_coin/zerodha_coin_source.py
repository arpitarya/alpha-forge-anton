"""Zerodha Coin — ETF + mutual fund holdings BrokerSource."""

from __future__ import annotations

import os

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import clear_session
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind, SourceStatus
from app.modules.brokers.zerodha_kite.zerodha_kite_instruments import (
    name_lookup,
    name_lookup_sync,
    type_lookup,
    type_lookup_sync,
)
from app.modules.brokers.zerodha_kite.zerodha_kite_source_helper import (
    acquire_enctoken,
    fetch_holdings_json as fetch_kite_holdings_json,
)
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


def _mf_holding_from_row(r: dict, slug: str) -> Holding:
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


def _etf_holding_from_row(r: dict, slug: str, names: dict[str, str] | None = None) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    invested, current = qty * avg, qty * ltp
    pnl = current - invested
    sym = str(r.get("tradingsymbol") or "").upper()
    return Holding(
        source=slug, asset_class=AssetClass.ETF,
        symbol=sym, name=(r.get("name") or (names or {}).get(sym)) or None,
        isin=r.get("isin"), quantity=qty, avg_price=avg, last_price=ltp,
        invested=invested, current_value=current, pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
        day_change_pct=float(r.get("day_change_percentage") or r.get("day_change_pct") or 0),
        exchange=r.get("exchange"),
    )


def _holding_from_csv(r: dict[str, str], slug: str) -> Holding:
    g = r.get
    invested = float(g("invested") or 0)
    pnl = float(g("pnl") or 0)
    ac_str = g("asset_class") or "mutual_fund"
    try:
        asset_class = AssetClass(ac_str)
    except ValueError:
        asset_class = AssetClass.MUTUAL_FUND
    return Holding(
        source=slug, asset_class=asset_class,
        symbol=str(g("tradingsymbol") or "").upper(), name=g("name") or None,
        isin=g("isin") or None, quantity=float(g("quantity") or 0),
        avg_price=float(g("average_price") or 0), last_price=float(g("last_price") or 0),
        invested=invested, current_value=float(g("current_value") or 0),
        pnl=pnl, pnl_pct=(pnl / invested * 100) if invested else float(g("pnl_pct") or 0),
        exchange=g("exchange") or None,
        day_change_pct=float(g("day_change_pct") or 0),
    )


class ZerodhaCoinSource(BrokerSource):
    slug = "zerodha_coin"
    label = "Zerodha (Coin)"
    kind = SourceKind.API
    notes = (
        "Log in to kite.zerodha.com inside the AlphaForge Anton Chrome "
        "(--remote-debugging-port=9299). Set ZERODHA_USER_ID in .env.cred.local. "
        "ETF holdings come from the Kite equity API; MF from the Coin API."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY
        self.refetch_seconds = int(os.getenv("ZERODHA_COIN_REFETCH_SECONDS", "3600"))

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("Zerodha Coin: %d ETF/MF holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug) for r in rows]

        # MF holdings from Coin API
        try:
            token = await acquire_token()
            mf_rows = await fetch_holdings_json(token)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (401, 403):
                logger.warning("Zerodha Coin: auth rejected (%s) — forcing re-login", status)
                clear_session("zerodha_coin")
                token = await acquire_token(force=True)
                mf_rows = await fetch_holdings_json(token)
            else:
                raise
        for r in mf_rows:
            r.setdefault("name", r.get("fund", ""))
            r.setdefault("asset_class", AssetClass.MUTUAL_FUND.value)

        # ETF holdings from Kite equity API
        etf_rows: list[dict] = []
        try:
            enctoken = await acquire_enctoken()
            kite_rows = await fetch_kite_holdings_json(enctoken)
            types = await type_lookup()
            names = await name_lookup()
            for r in kite_rows:
                sym = str(r.get("tradingsymbol") or "").upper()
                if not r.get("name"):
                    r["name"] = names.get(sym, "")
                if types.get(sym, "EQ").upper() == "ETF":
                    r["asset_class"] = AssetClass.ETF.value
                    etf_rows.append(r)
        except Exception as e:
            logger.warning("Zerodha Coin: ETF fetch failed (%s) — MF only", e)

        all_rows = etf_rows + mf_rows
        write_csv(all_rows, live_csv_path())
        etf = [_etf_holding_from_row(r, self.slug) for r in etf_rows]
        mf = [_mf_holding_from_row(r, self.slug) for r in mf_rows]
        out = etf + mf
        logger.info("Zerodha Coin: %d ETF + %d MF → cached to CSV", len(etf), len(mf))
        return out
