"""Wint Wealth holdings — BrokerSource over CDP browser fetch + CSV cache.

Primarily bonds/NCDs/SGBs. `asset_type` from the normalizer drives AssetClass;
CSV-cached rows default to BOND (asset_type is not stored in the shared CSV schema).
"""

from __future__ import annotations

from typing import IO

from app.core.logging import get_logger
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind, SourceStatus
from app.modules.brokers.wintwealth.wintwealth_csv import WintWealthCSVSource as _CSV
from app.modules.brokers.wintwealth.wintwealth_dump import is_csv_fresh, live_csv_path, read_csv, write_csv
from app.modules.brokers.wintwealth.wintwealth_source_helper import REQUIRED_ENV, env, fetch_holdings_via_browser

logger = get_logger("brokers.wintwealth")
__all__ = ["WintWealthSource", "REQUIRED_ENV", "env"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    inv = qty * avg
    cur = qty * ltp
    pnl = cur - inv
    asset_class = AssetClass.GOLD if r.get("asset_type") == "gold" else AssetClass.BOND
    return Holding(
        source=slug, asset_class=asset_class,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        name=r.get("name") or None,
        isin=r.get("isin") or None,
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=inv, current_value=cur, pnl=pnl,
        pnl_pct=(pnl / inv * 100) if inv else 0.0,
        exchange=r.get("exchange") or None,
    )


def _holding_from_csv(r: dict[str, str], slug: str) -> Holding:
    g = r.get
    return Holding(
        source=slug, asset_class=AssetClass.BOND,
        symbol=str(g("tradingsymbol") or "").upper(),
        name=g("name") or None, isin=g("isin") or None,
        quantity=float(g("quantity") or 0), avg_price=float(g("average_price") or 0),
        last_price=float(g("last_price") or 0), invested=float(g("invested") or 0),
        current_value=float(g("current_value") or 0), pnl=float(g("pnl") or 0),
        pnl_pct=float(g("pnl_pct") or 0), exchange=g("exchange") or None,
    )


class WintWealthSource(BrokerSource):
    slug = "wintwealth"
    label = "Wint Wealth"
    kind = SourceKind.API
    notes = (
        "Manual login: log in to wintwealth.com inside the AlphaForge Chrome "
        "(started with --remote-debugging-port=9299). AlphaForge never "
        "stores your password or OTP. Set WINTWEALTH_USER_ID in .env.cred.local."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        holdings = _CSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("WintWealth: %d holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug) for r in rows]
        try:
            rows = await fetch_holdings_via_browser()
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ("login", "expired", "401", "403")):
                logger.warning("WintWealth: fetch failed (%s) — retrying with forced login", e)
                rows = await fetch_holdings_via_browser(force_login=True)
            else:
                raise
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("WintWealth: fetched %d holdings → cached to CSV", len(out))
        return out
