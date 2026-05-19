"""Angel One — CDP login + holdings fetch via the authenticated browser context.

SmartAPI's free tier proved unreliable for personal portfolio sync (rate
limits, TOTP friction, 401s on long-lived JWTs). We instead attach to the
running Chrome, navigate to the holdings page, and capture the XHR response
Angel One's own web app makes — same pattern as Groww and Wint Wealth.

Probe-confirmed endpoint (see [probes/angelone_probe.py](../../../../../../probes/angelone_probe.py)):
    POST https://portfolio-prod.angelone.in/family/v2/superportfolio
    body {partyCode, partyCodeList} → data.EquityPortfolio.HoldingDetail[]

Login flow: user logs in to angelone.in inside Chrome started with
--remote-debugging-port=9299.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page
from app.modules.brokers.broker_urls import (
    ANGELONE_HOLDINGS_PAGE as HOLDINGS_PAGE,
    ANGELONE_HOLDINGS_URL_NEEDLE as _HOLDINGS_URL_NEEDLE,
    ANGELONE_LOGIN_URL as LOGIN_URL,
)

logger = get_logger("brokers.angelone_helper")

REQUIRED_ENV: tuple[str, ...] = ("ANGELONE_CLIENT_ID",)

_CDP_WAIT_SECONDS = int(os.getenv("ANGELONE_LOGIN_CDP_WAIT", "180"))


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
    if "/login" not in page.url and "login.angelone" not in page.url:
        return
    logger.info("Angel One: waiting up to %ss for manual login", wait_seconds)
    await page.wait_for_url(
        lambda url: "/login" not in url and "angelone.in" in url,
        timeout=wait_seconds * 1000,
    )


def _extract_equity_holdings(payload: Any) -> list[dict[str, Any]]:
    """Drill into the superportfolio response to pull out HoldingDetail rows."""
    if not isinstance(payload, dict):
        return []
    data = payload.get("data") or {}
    if not isinstance(data, dict):
        return []
    out: list[dict[str, Any]] = []
    # Equity is the only segment AlphaForge Anton surfaces from Angel One today.
    # Bonds/SGBs/MFs live under their own keys with identical shape if needed
    # later: BondsPortfolio.HoldingDetail / SGBPortfolio.HoldingDetail.
    equity = data.get("EquityPortfolio") or {}
    if isinstance(equity, dict):
        rows = equity.get("HoldingDetail") or []
        if isinstance(rows, list):
            out.extend(r for r in rows if isinstance(r, dict))
    return out


def normalize(row: dict[str, Any]) -> dict[str, Any]:
    """Map a superportfolio HoldingDetail row to the shared dict shape."""
    qty = _to_float(row.get("qty") or row.get("total_qty") or row.get("AvlQty"))
    avg = _to_float(row.get("avgPrice") or row.get("baseAvgPrice"))
    ltp = _to_float(row.get("ltp"))
    name = row.get("compName") or row.get("details") or ""
    # tradeSymbol disambiguates series variants (e.g. PGINVIT-IV vs PGINVIT).
    # Fall back to symbolName if the row predates the series suffix.
    symbol = str(row.get("tradeSymbol") or row.get("symbolName") or "").upper()
    return {
        "tradingsymbol": symbol,
        "name": str(name).strip(),
        "isin": row.get("isin") or "",
        "exchange": row.get("exchName") or "NSE",
        "quantity": qty,
        "average_price": avg,
        "last_price": ltp or avg,
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
        rows = _extract_equity_holdings(body)
        if rows:
            fut.set_result(rows)

    page.on("response", on_response)
    try:
        try:
            await page.reload(wait_until="domcontentloaded", timeout=20000)
        except Exception as e:  # noqa: BLE001
            logger.warning("Angel One: reload warning: %s — waiting for XHR", e)
        try:
            return await asyncio.wait_for(fut, timeout=timeout_seconds)
        except TimeoutError as e:
            raise RuntimeError(
                "Angel One: superportfolio response not seen within "
                f"{timeout_seconds:.0f}s — login may have expired."
            ) from e
    finally:
        page.remove_listener("response", on_response)


async def fetch_holdings_via_browser(
    *, force_login: bool = False
) -> list[dict[str, Any]]:
    pw, browser = await connect_existing_chrome()
    try:
        target = LOGIN_URL if force_login else HOLDINGS_PAGE
        page = await find_or_open_page(browser, target, "angelone.in")
        await _ensure_logged_in(page, _CDP_WAIT_SECONDS)
        if "/portfolio/equity" not in page.url and "/portfolio" not in page.url:
            try:
                await page.goto(HOLDINGS_PAGE, wait_until="domcontentloaded", timeout=20000)
            except Exception as e:  # noqa: BLE001
                logger.warning("Angel One: nav to holdings failed (%s); proceeding", e)
        raw = await _capture_holdings_via_reload(page)
        logger.info("Angel One: captured %d equity holdings via CDP", len(raw))
        return [normalize(r) for r in raw]
    finally:
        await browser.close()
        await pw.stop()
