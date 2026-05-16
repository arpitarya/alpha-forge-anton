"""Ticker Tape — CDP login + digital-gold holdings fetch.

Confirmed endpoints (probed 2026-05-16):
  gold.api.tickertape.in/profile/v2   → goldBalance, averageBuyPrice, goldExponent, priceExponent
  gold.api.tickertape.in/price?type=BUY → currentPrice (₹/gram)

Both fire on page load at TICKERTAPE_GOLD_PAGE. We capture them in parallel and
combine into a single DIGITAL_GOLD holding row.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page
from app.modules.brokers.broker_urls import (
    TICKERTAPE_GOLD_PAGE,
    TICKERTAPE_GOLD_PRICE_NEEDLE,
    TICKERTAPE_GOLD_PROFILE_NEEDLE,
    TICKERTAPE_LOGIN_URL,
)

logger = get_logger("brokers.tickertape_helper")

HOLDINGS_PAGE = TICKERTAPE_GOLD_PAGE
LOGIN_URL = TICKERTAPE_LOGIN_URL
REQUIRED_ENV: tuple[str, ...] = ("TICKERTAPE_USER_ID",)

_CDP_WAIT_SECONDS = int(os.getenv("TICKERTAPE_LOGIN_CDP_WAIT", "180"))


def env(key: str) -> str:
    return os.getenv(key, "").strip()


def _to_float(v: Any) -> float:
    if v in (None, ""):
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


async def _ensure_logged_in(page: Any, wait_seconds: int) -> None:
    if "/login" not in page.url and "/auth" not in page.url:
        return
    logger.info("Ticker Tape: waiting up to %ss for manual login", wait_seconds)
    await page.wait_for_url(
        lambda url: "/login" not in url and "tickertape.in" in url,
        timeout=wait_seconds * 1000,
    )


def normalize_gold(profile: dict[str, Any], price: dict[str, Any]) -> dict[str, Any]:
    """Convert profile/v2 + price response into a single holding dict."""
    exp_g = int(profile.get("goldExponent", -4))
    exp_p = int(profile.get("priceExponent", -2))
    qty = _to_float(profile.get("goldBalance")) * (10 ** exp_g)
    avg = _to_float(profile.get("averageBuyPrice")) * (10 ** exp_p)
    ltp = _to_float(price.get("currentPrice"))
    inv = round(qty * avg, 2)
    cur = round(qty * ltp, 2)
    pnl = round(cur - inv, 2)
    return {
        "tradingsymbol": "DIGITAL_GOLD",
        "name": "Digital Gold (SafeGold via Ticker Tape)",
        "isin": "",
        "exchange": None,
        "quantity": round(qty, 6),
        "average_price": round(avg, 2),
        "last_price": round(ltp, 2),
        "invested": inv,
        "current_value": cur,
        "pnl": pnl,
        "pnl_pct": round((pnl / inv * 100) if inv else 0.0, 4),
    }


async def _capture_gold_data(page: Any, timeout: float = 20.0) -> dict[str, Any]:
    loop = asyncio.get_event_loop()
    profile_fut: asyncio.Future[dict] = loop.create_future()
    price_fut: asyncio.Future[dict] = loop.create_future()

    async def on_response(resp: Any) -> None:
        if resp.status != 200:
            return
        try:
            body = await resp.json()
        except Exception:  # noqa: BLE001
            return
        if TICKERTAPE_GOLD_PROFILE_NEEDLE in resp.url and not profile_fut.done():
            data = (body or {}).get("data")
            if data:
                profile_fut.set_result(data)
        elif TICKERTAPE_GOLD_PRICE_NEEDLE in resp.url and not price_fut.done():
            data = (body or {}).get("data")
            if data:
                price_fut.set_result(data)

    page.on("response", on_response)
    try:
        try:
            await page.reload(wait_until="domcontentloaded", timeout=20000)
        except Exception as e:  # noqa: BLE001
            logger.warning("Ticker Tape: reload warning: %s", e)
        try:
            profile, price = await asyncio.wait_for(
                asyncio.gather(profile_fut, price_fut), timeout=timeout
            )
        except TimeoutError as e:
            raise RuntimeError(
                f"Ticker Tape: gold data XHR not seen within {timeout:.0f}s — "
                "login may have expired or TICKERTAPE_GOLD_PROFILE_NEEDLE is wrong."
            ) from e
    finally:
        page.remove_listener("response", on_response)
    return {"profile": profile, "price": price}


async def fetch_holdings_via_browser(*, force_login: bool = False) -> list[dict[str, Any]]:
    pw, browser = await connect_existing_chrome()
    try:
        target = LOGIN_URL if force_login else HOLDINGS_PAGE
        page = await find_or_open_page(browser, target, "tickertape.in")
        await _ensure_logged_in(page, _CDP_WAIT_SECONDS)
        data = await _capture_gold_data(page)
        row = normalize_gold(data["profile"], data["price"])
        logger.info(
            "Ticker Tape: %.4fg gold @ avg ₹%.2f ltp ₹%.2f pnl %.2f%%",
            row["quantity"], row["average_price"], row["last_price"], row["pnl_pct"],
        )
        return [row]
    finally:
        await browser.close()
        await pw.stop()
