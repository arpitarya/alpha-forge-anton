"""INDmoney — CDP login + US-stocks holdings fetch via the authenticated browser context.

INDmoney exposes no free public API; we attach to the running Chrome, navigate
to the US stocks portfolio page, and capture the XHR the web app fires —
same pattern as Groww / Angel One.

Confirmed holdings endpoint (probed 2026-05-25):
  apixt-fz.indmoney.com/us-stock-broker/us/portfolio/equity/summary?response_format=json
Response shape: {"demat_summary": {"asset_summary": {"scrip_details": [
  {"metadata": {symbol, name, live_price, day_change_percentage, sector, ...},
   "holdings": {quantity, avg_price, invested_amount, current_value,
                overall_pnl, overall_pnl_percentage, ...}}, ...]}}}
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page
from app.modules.brokers.broker_env import require_env
from app.modules.brokers.broker_urls import (
    INDMONEY_HOLDINGS_PAGE as HOLDINGS_PAGE,
    INDMONEY_HOLDINGS_URL_NEEDLE as _HOLDINGS_URL_NEEDLE,
    INDMONEY_LOGIN_URL as LOGIN_URL,
)

logger = get_logger("brokers.indmoney_helper")

REQUIRED_ENV: tuple[str, ...] = ("INDMONEY_USER_ID",)

_CDP_WAIT_SECONDS = int(os.getenv("INDMONEY_LOGIN_CDP_WAIT", "180"))


def env(key: str) -> str:
    return os.getenv(key, "").strip()


def _to_float(v: Any) -> float:
    if v in (None, ""):
        return 0.0
    if isinstance(v, str):
        v = v.replace(",", "").strip()
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


async def _ensure_logged_in(page: Any, wait_seconds: int) -> None:
    if "/login" not in page.url and "/auth" not in page.url:
        return
    logger.info("INDmoney: waiting up to %ss for manual login", wait_seconds)
    await page.wait_for_url(
        lambda url: "/login" not in url and "indmoney.com" in url,
        timeout=wait_seconds * 1000,
    )


def _extract_holdings(payload: Any) -> list[dict[str, Any]]:
    """Extract the list of holding rows from the holdings XHR payload."""
    if isinstance(payload, dict):
        # Current API shape (2026-05-25): demat_summary → asset_summary → scrip_details
        demat = payload.get("demat_summary")
        if isinstance(demat, dict):
            asset = demat.get("asset_summary")
            if isinstance(asset, dict):
                scrips = asset.get("scrip_details")
                if isinstance(scrips, list):
                    return [r for r in scrips if isinstance(r, dict)]
        # Legacy shape: {"data": [...]}
        v = payload.get("data")
        if isinstance(v, list):
            return [r for r in v if isinstance(r, dict)]
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    return []


def normalize(row: dict[str, Any]) -> dict[str, Any]:
    """Map an INDmoney holding row (new or legacy shape) to the shared dict shape."""
    meta = row.get("metadata") or {}
    hold = row.get("holdings") or {}
    # New API: row = {metadata: {...}, holdings: {...}}
    # Legacy API: flat dict with ticker/avg_price/live_price keys

    qty = _to_float(hold.get("quantity") or row.get("quantity"))
    avg = _to_float(hold.get("avg_price") or row.get("avg_price"))
    ltp = _to_float(meta.get("live_price") or row.get("live_price"))
    inv = _to_float(hold.get("invested_amount") or row.get("invested_amount")) or (qty * avg)
    cur = _to_float(hold.get("current_value") or row.get("current_value")) or (qty * ltp)
    pnl = _to_float(hold.get("overall_pnl") or row.get("total_profit_loss")) or (cur - inv)
    pnl_pct = (
        _to_float(hold.get("overall_pnl_percentage") or row.get("total_percent_change"))
        or ((pnl / inv * 100) if inv else 0.0)
    )
    day_change_pct = _to_float(
        meta.get("day_change_percentage") or row.get("day_change_percentage")
    )
    return {
        "tradingsymbol": str(
            meta.get("symbol") or meta.get("ind_key") or row.get("ticker") or ""
        ).upper(),
        "name": str(meta.get("name") or row.get("name") or "").strip() or None,
        "isin": meta.get("isin") or row.get("isin") or "",
        "exchange": "NYSE",
        "quantity": qty,
        "average_price": avg,
        "last_price": ltp,
        "invested": inv,
        "current_value": cur,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "day_change_pct": day_change_pct,
        "sector": meta.get("sector") or row.get("sector") or None,
    }


async def _capture_holdings_via_reload(
    page: Any, timeout_seconds: float = 30.0
) -> list[dict[str, Any]]:
    fut: asyncio.Future[list[dict[str, Any]]] = asyncio.get_event_loop().create_future()

    async def on_response(resp: Any) -> None:
        if _HOLDINGS_URL_NEEDLE not in resp.url:
            return
        if resp.status != 200 or fut.done():
            return
        try:
            body = await resp.json()
        except Exception:  # noqa: BLE001
            return
        rows = _extract_holdings(body)
        if rows:
            fut.set_result(rows)

    page.on("response", on_response)
    try:
        try:
            await page.reload(wait_until="domcontentloaded", timeout=20000)
        except Exception as e:  # noqa: BLE001
            logger.warning("INDmoney: reload warning: %s — waiting for XHR", e)
        try:
            return await asyncio.wait_for(fut, timeout=timeout_seconds)
        except TimeoutError as e:
            raise RuntimeError(
                "INDmoney: holdings XHR not seen within "
                f"{timeout_seconds:.0f}s — login may have expired or "
                "_HOLDINGS_URL_NEEDLE is wrong (run probes/indmoney_probe.py)."
            ) from e
    finally:
        page.remove_listener("response", on_response)


async def fetch_holdings_via_browser(
    *, force_login: bool = False
) -> list[dict[str, Any]]:
    require_env("INDMONEY_USER_ID", env)
    pw, browser = await connect_existing_chrome()
    try:
        target = LOGIN_URL if force_login else HOLDINGS_PAGE
        page = await find_or_open_page(browser, target, "indmoney.com")
        await _ensure_logged_in(page, _CDP_WAIT_SECONDS)
        raw = await _capture_holdings_via_reload(page)
        logger.info("INDmoney: captured %d holdings via CDP", len(raw))
        return [normalize(r) for r in raw]
    finally:
        await browser.close()
        await pw.stop()
