"""Zerodha Kite — manual CDP login + enctoken cache + holdings fetch.

Login flow: the user logs in to kite.zerodha.com inside a Chrome instance
started with `--remote-debugging-port=9299` (loopback only, see _cdp.py).
This helper attaches over CDP, reuses the enctoken cookie if already
authenticated, otherwise waits up to ZERODHA_LOGIN_CDP_WAIT seconds for
the user to complete login manually. No password / TOTP secret is ever
stored or read by AlphaForge Anton.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome, cookie_value, find_or_open_page
from app.modules.brokers._http import load_session, make_client, save_session
from app.modules.brokers.broker_env import require_env
from app.modules.brokers.broker_urls import (
    ZERODHA_COIN_HOLDINGS_PATH,
    ZERODHA_HOLDINGS_PATH,
    ZERODHA_KITE_BASE,
    ZERODHA_LOGIN_URL,
    ZERODHA_MARGINS_PATH,
)

logger = get_logger("brokers.zerodha_kite_helper")

KITE_BASE = ZERODHA_KITE_BASE
HOLDINGS_PATH = ZERODHA_HOLDINGS_PATH
MARGINS_PATH = ZERODHA_MARGINS_PATH
COIN_HOLDINGS_PATH = ZERODHA_COIN_HOLDINGS_PATH
REQUIRED_ENV: tuple[str, ...] = ("ZERODHA_USER_ID",)

_LOGIN_URL = ZERODHA_LOGIN_URL
_CDP_WAIT_SECONDS = int(os.getenv("ZERODHA_LOGIN_CDP_WAIT", "180"))


def env(key: str) -> str:
    return os.getenv(key, "").strip()

async def cdp_login(wait_seconds: int = _CDP_WAIT_SECONDS) -> str:
    """Acquire enctoken from an already-running Chrome (CDP, port 9299).

    If the user is already logged in inside that Chrome, the enctoken cookie
    is read directly. Otherwise we open kite.zerodha.com in that browser and
    wait up to `wait_seconds` for the user to finish login manually.
    """
    pw, browser = await connect_existing_chrome()
    try:
        page = await find_or_open_page(browser, _LOGIN_URL, "kite.zerodha.com")
        ctx = page.context
        token = await cookie_value(ctx, "enctoken", "kite.zerodha.com")
        if token:
            logger.info("Zerodha: reused enctoken from attached Chrome session")
            return token
        logger.info("Zerodha: waiting up to %ss for manual login in attached Chrome", wait_seconds)
        await page.wait_for_url("**/dashboard**", timeout=wait_seconds * 1000)
        token = await cookie_value(ctx, "enctoken", "kite.zerodha.com")
        if not token:
            raise RuntimeError("Zerodha login completed but no enctoken cookie was found")
        return token
    finally:
        await browser.close()
        await pw.stop()


async def acquire_enctoken(force: bool = False) -> str:
    cached = load_session("zerodha")
    if not force and cached.get("enctoken"):
        return str(cached["enctoken"])

    user_id = require_env("ZERODHA_USER_ID", env)
    enctoken = await cdp_login()
    save_session("zerodha", {"enctoken": enctoken, "user_id": user_id})
    logger.info("Zerodha: acquired new enctoken via CDP-attached Chrome")
    return enctoken


async def fetch_margins_json(enctoken: str) -> dict[str, Any]:
    """GET /oms/user/margins → equity available cash for the Kite account."""
    headers = {"Authorization": f"enctoken {enctoken}", "X-Kite-Version": "3"}
    async with make_client(base_url=KITE_BASE, headers=headers) as client:
        client.cookies.set("enctoken", enctoken, domain="kite.zerodha.com")
        res = await client.get(MARGINS_PATH)
        if res.status_code in (401, 403):
            raise httpx.HTTPStatusError(
                f"enctoken rejected ({res.status_code})", request=res.request, response=res
            )
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Zerodha margins failed: {payload.get('message') or payload}")
    return dict(payload.get("data") or {})


async def fetch_mf_holdings_json(enctoken: str) -> list[dict[str, Any]]:
    """GET /api/mf/holdings → COIN mutual fund holdings (empty list if not subscribed)."""
    headers = {"Authorization": f"enctoken {enctoken}", "X-Kite-Version": "3"}
    async with make_client(base_url=KITE_BASE, headers=headers) as client:
        client.cookies.set("enctoken", enctoken, domain="kite.zerodha.com")
        res = await client.get(COIN_HOLDINGS_PATH)
        if res.status_code in (401, 403):
            raise httpx.HTTPStatusError(
                f"enctoken rejected ({res.status_code})", request=res.request, response=res
            )
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Zerodha COIN MF failed: {payload.get('message') or payload}")
    return list(payload.get("data") or [])


async def fetch_holdings_json(enctoken: str) -> list[dict[str, Any]]:
    headers = {
        "Authorization": f"enctoken {enctoken}",
        "X-Kite-Version": "3",
    }
    async with make_client(base_url=KITE_BASE, headers=headers) as client:
        client.cookies.set("enctoken", enctoken, domain="kite.zerodha.com")
        res = await client.get(HOLDINGS_PATH)
        if res.status_code in (401, 403):
            raise httpx.HTTPStatusError(
                f"enctoken rejected ({res.status_code})", request=res.request, response=res
            )
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Zerodha holdings failed: {payload.get('message') or payload}")
    return list(payload.get("data") or [])
