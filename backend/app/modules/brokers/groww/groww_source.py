"""Groww holdings — BrokerSource impl over CDP browser fetch + CSV cache.

Auth flow: user logs in to groww.in inside the AlphaForge Chrome instance
started with --remote-debugging-port=9299. `fetch()` attaches over CDP,
runs the holdings API call inside the authenticated page, and caches the
result to CSV. Subsequent `fetch()` calls within GROWW_REFETCH_SECONDS
return from the CSV cache without re-launching Chrome.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import IO

from app.core.logging import get_logger
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
    WalletBalance,
)
from app.modules.brokers.groww.groww_csv import GrowwCSVSource as _GrowwCSV
from app.modules.brokers.groww.groww_cash_helper import capture_groww_cash
from app.modules.brokers.groww.groww_dump import (
    is_csv_fresh,
    live_csv_path,
    read_csv,
    write_csv,
)
from app.modules.brokers.groww.groww_source_helper import (
    REQUIRED_ENV,
    env,
    fetch_holdings_via_browser,
)

logger = get_logger("brokers.groww")

__all__ = ["REQUIRED_ENV", "GrowwSource", "env"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    invested = qty * avg
    current = qty * ltp
    pnl = current - invested
    return Holding(
        source=slug,
        asset_class=AssetClass.EQUITY,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        name=r.get("name") or None,
        isin=r.get("isin") or None,
        quantity=qty,
        avg_price=avg,
        last_price=ltp,
        invested=invested,
        current_value=current,
        pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
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


class GrowwSource(BrokerSource):
    slug = "groww"
    label = "Groww"
    kind = SourceKind.API
    supports_cash = True
    notes = (
        "Manual login: log in to groww.in inside the AlphaForge Chrome "
        "(started with --remote-debugging-port=9299). AlphaForge never "
        "stores your password or OTP. Set GROWW_USER_ID in .env.cred.local."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        holdings = _GrowwCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("Groww: %d holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug) for r in rows]

        try:
            rows = await fetch_holdings_via_browser()
        except Exception as e:
            # Auth-class failures: prompt a re-login on next try
            msg = str(e).lower()
            if any(k in msg for k in ("401", "403", "login", "no candidate endpoint")):
                logger.warning(
                    "Groww: fetch failed (%s) — retrying with forced login", e
                )
                rows = await fetch_holdings_via_browser(force_login=True)
            else:
                raise

        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("Groww: fetched %d holdings → cached to CSV", len(out))
        return out

    async def fetch_cash(self) -> WalletBalance:
        cash = await capture_groww_cash()
        logger.info("Groww: captured wallet cash ₹%.2f via CDP", cash)
        return WalletBalance(
            source=self.slug, currency="INR", cash=round(cash, 2),
            as_of=datetime.now(UTC),
        )
