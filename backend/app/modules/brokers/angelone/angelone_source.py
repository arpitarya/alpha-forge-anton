"""Angel One holdings — BrokerSource impl over CDP browser fetch + CSV cache.

Auth flow: user logs in to angelone.in inside the AlphaForge Chrome instance
started with --remote-debugging-port=9299. `fetch()` attaches over CDP, runs
the holdings API call inside the authenticated page, and caches the result to
CSV. Subsequent `fetch()` calls within ANGELONE_REFETCH_SECONDS return from
the CSV cache without re-launching Chrome.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import IO

from app.core.logging import get_logger
from app.modules.brokers.angelone.angelone_cash_helper import capture_angelone_cash
from app.modules.brokers.angelone.angelone_dump import (
    is_csv_fresh,
    live_csv_path,
    read_csv,
    write_csv,
)
from app.modules.brokers.angelone.angelone_source_helper import (
    REQUIRED_ENV,
    env,
    fetch_holdings_via_browser,
)
from app.modules.brokers.angelone.angelone_csv import AngelOneCSVSource as _AngelOneCSV
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
    WalletBalance,
)

logger = get_logger("brokers.angelone")

__all__ = ["REQUIRED_ENV", "AngelOneSource", "env"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    inv = qty * avg
    cur = qty * ltp
    pnl = cur - inv
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        name=r.get("name") or None,
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
    label = "Angel One"
    kind = SourceKind.API
    supports_cash = True
    notes = (
        "Manual login: log in to angelone.in inside the AlphaForge Chrome "
        "(started with --remote-debugging-port=9299). AlphaForge never "
        "stores your password or TOTP. Set ANGELONE_CLIENT_ID in .env.cred.local."
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
            rows = await fetch_holdings_via_browser()
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ("401", "403", "login", "expired")):
                logger.warning("Angel One: fetch failed (%s) — retrying with forced login", e)
                rows = await fetch_holdings_via_browser(force_login=True)
            else:
                raise
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("Angel One: fetched %d holdings → cached to CSV", len(out))
        return out

    async def fetch_cash(self) -> WalletBalance:
        cash = await capture_angelone_cash()
        logger.info("Angel One: captured wallet cash ₹%.2f via CDP", cash)
        return WalletBalance(
            source=self.slug, currency="INR", cash=round(cash, 2),
            as_of=datetime.now(UTC),
        )
