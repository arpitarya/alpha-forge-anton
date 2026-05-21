"""Binance — CDP login + spot-wallet holdings (BTC-quoted, converted to USD)."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page
from app.modules.brokers.broker_urls import BINANCE_HOLDINGS_PAGE as HOLDINGS_PAGE
from app.modules.brokers.broker_urls import BINANCE_HOLDINGS_URL_NEEDLES as _NEEDLES
from app.modules.brokers.broker_urls import BINANCE_LOGIN_URL as LOGIN_URL

logger = get_logger("brokers.binance_helper")
REQUIRED_ENV: tuple[str, ...] = ("BINANCE_USER_ID",)
_CDP_WAIT_SECONDS = int(os.getenv("BINANCE_LOGIN_CDP_WAIT", "180"))
_BTC_USD_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"


def env(key: str) -> str:
    return os.getenv(key, "").strip()


def _f(v: Any) -> float:
    if v in (None, ""): return 0.0
    if isinstance(v, str): v = v.replace(",", "").strip()
    try: return float(v)
    except (TypeError, ValueError): return 0.0


async def _ensure_logged_in(page: Any, wait_seconds: int) -> None:
    if "/login" not in page.url and "accounts.binance.com" not in page.url: return
    logger.info("Binance: waiting up to %ss for manual login", wait_seconds)
    await page.wait_for_url(
        lambda url: "/login" not in url and "binance.com" in url,
        timeout=wait_seconds * 1000,
    )


async def _btc_usd() -> float:
    async with httpx.AsyncClient(timeout=5) as c:
        r = await c.get(_BTC_USD_URL); r.raise_for_status()
        return _f(r.json().get("price"))


def _extract_assets(p: Any) -> list[dict[str, Any]]:
    v = p.get("data") if isinstance(p, dict) else p
    return [r for r in v if isinstance(r, dict)] if isinstance(v, list) else []


def normalize(row: dict[str, Any], btc_usd: float) -> dict[str, Any]:
    qty = _f(row.get("free")) + _f(row.get("locked")) + _f(row.get("freeze"))
    cur = _f(row.get("btcValuation")) * btc_usd
    return {
        "tradingsymbol": str(row.get("asset") or "").upper(),
        "name": str(row.get("assetFullName") or "").strip() or None,
        "isin": "", "exchange": "BINANCE", "sector": "Crypto",
        "quantity": qty, "average_price": 0.0,
        "last_price": (cur / qty) if qty else 0.0,
        "invested": cur, "current_value": cur, "pnl": 0.0, "pnl_pct": 0.0,
    }


async def _capture(page: Any, timeout_seconds: float = 30.0) -> list[dict[str, Any]]:
    fut: asyncio.Future[list[dict[str, Any]]] = asyncio.get_event_loop().create_future()

    async def on_response(resp: Any) -> None:
        if not any(n in resp.url for n in _NEEDLES) or resp.status != 200 or fut.done(): return
        try: body = await resp.json()
        except Exception: return  # noqa: BLE001
        rows = _extract_assets(body)
        if rows: fut.set_result(rows)

    page.on("response", on_response)
    try:
        try: await page.reload(wait_until="domcontentloaded", timeout=20000)
        except Exception as e: logger.warning("Binance: reload warning: %s", e)  # noqa: BLE001
        try: return await asyncio.wait_for(fut, timeout=timeout_seconds)
        except TimeoutError as e:
            raise RuntimeError(f"Binance: wallet XHR not seen in {timeout_seconds:.0f}s — login expired or needles wrong (probes/binance_probe.py).") from e
    finally:
        page.remove_listener("response", on_response)


async def fetch_holdings_via_browser(*, force_login: bool = False) -> list[dict[str, Any]]:
    pw, browser = await connect_existing_chrome()
    try:
        page = await find_or_open_page(browser, LOGIN_URL if force_login else HOLDINGS_PAGE, "binance.com")
        await _ensure_logged_in(page, _CDP_WAIT_SECONDS)
        raw = await _capture(page)
        logger.info("Binance: captured %d wallet rows via CDP", len(raw))
        btc_usd = await _btc_usd()
        return [normalize(r, btc_usd) for r in raw if _f(r.get("btcValuation")) > 0]
    finally:
        await browser.close(); await pw.stop()
