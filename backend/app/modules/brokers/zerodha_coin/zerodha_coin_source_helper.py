"""Zerodha Coin — MF holdings via the same enctoken as Kite.

Login flow: user logs in to kite.zerodha.com inside Chrome
(--remote-debugging-port=9299). This helper re-uses the enctoken cookie
from that session to call the Coin MF API — no separate Coin login needed.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome, cookie_value, find_or_open_page
from app.modules.brokers._http import load_session, make_client, save_session
from app.modules.brokers.broker_urls import (
    ZERODHA_COIN_HOLDINGS_PATH,
    ZERODHA_KITE_BASE,
    ZERODHA_LOGIN_URL,
)

logger = get_logger("brokers.zerodha_coin_helper")

KITE_BASE = ZERODHA_KITE_BASE
COIN_HOLDINGS_PATH = ZERODHA_COIN_HOLDINGS_PATH
REQUIRED_ENV: tuple[str, ...] = ("ZERODHA_USER_ID",)

_LOGIN_URL = ZERODHA_LOGIN_URL
_CDP_WAIT_SECONDS = int(os.getenv("ZERODHA_LOGIN_CDP_WAIT", "180"))


def env(key: str) -> str:
    return os.getenv(key, "").strip()


async def _cdp_acquire_enctoken(wait_seconds: int = _CDP_WAIT_SECONDS) -> str:
    pw, browser = await connect_existing_chrome()
    try:
        page = await find_or_open_page(browser, _LOGIN_URL, "kite.zerodha.com")
        ctx = page.context
        token = await cookie_value(ctx, "enctoken", "kite.zerodha.com")
        if token:
            logger.info("Zerodha Coin: reused enctoken from attached Chrome session")
            return token
        logger.info("Zerodha Coin: waiting up to %ss for manual Kite login", wait_seconds)
        await page.wait_for_url("**/dashboard**", timeout=wait_seconds * 1000)
        token = await cookie_value(ctx, "enctoken", "kite.zerodha.com")
        if not token:
            raise RuntimeError("Zerodha login completed but no enctoken cookie was found")
        return token
    finally:
        await browser.close()
        await pw.stop()


async def acquire_token(force: bool = False) -> str:
    cached = load_session("zerodha_coin")
    if not force and cached.get("enctoken"):
        return str(cached["enctoken"])
    if not env("ZERODHA_USER_ID"):
        raise RuntimeError(
            "ZERODHA_USER_ID not set in .env.cred.local — fill it in before running."
        )
    enctoken = await _cdp_acquire_enctoken()
    save_session("zerodha_coin", {"enctoken": enctoken, "user_id": env("ZERODHA_USER_ID")})
    logger.info("Zerodha Coin: acquired enctoken via CDP-attached Chrome")
    return enctoken


async def fetch_holdings_json(token: str) -> list[dict[str, Any]]:
    """GET /api/mf/holdings → COIN mutual fund holdings list."""
    headers = {"Authorization": f"enctoken {token}", "X-Kite-Version": "3"}
    async with make_client(base_url=KITE_BASE, headers=headers) as client:
        client.cookies.set("enctoken", token, domain="kite.zerodha.com")
        res = await client.get(COIN_HOLDINGS_PATH)
        if res.status_code in (401, 403):
            raise httpx.HTTPStatusError(
                f"enctoken rejected ({res.status_code})", request=res.request, response=res
            )
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Zerodha Coin MF holdings failed: {payload.get('message') or payload}")
    return list(payload.get("data") or [])
