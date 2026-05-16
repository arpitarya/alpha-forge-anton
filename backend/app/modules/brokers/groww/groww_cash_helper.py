"""Groww — capture free-cash balance via CDP from a fresh tab.

Groww's balance APIs need the same client-side HMAC checksum + JWT as the
holdings call, so we use the same trick: open a new tab to a page that
fetches the balance, register a response listener, and read the figure off
the wire. The page is closed when we're done so it doesn't linger in the
user's Chrome.
"""

from __future__ import annotations

import asyncio
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome
from app.modules.brokers.broker_urls import (
    GROWW_BALANCE_PAGE as BALANCE_PAGE,
    GROWW_BALANCE_URL_NEEDLES as _BALANCE_URL_NEEDLES,
)

logger = get_logger("brokers.groww_cash")


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _scan_for_cash(node: Any) -> float | None:
    """Pluck CASH.value from /margin/user_margin_details — label 'Cash'."""
    if isinstance(node, dict):
        cash = node.get("CASH")
        if isinstance(cash, dict) and "value" in cash:
            return _to_float(cash["value"])
    return None


async def capture_groww_cash(timeout_seconds: float = 20.0) -> float:
    """Open a fresh Groww tab, capture balance from the first matching XHR, close it."""
    pw, browser = await connect_existing_chrome()
    cash_future: asyncio.Future[float] = asyncio.get_event_loop().create_future()
    page = None
    try:
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await ctx.new_page()

        async def on_response(resp: Any) -> None:
            url = resp.url
            if not any(n in url for n in _BALANCE_URL_NEEDLES):
                return
            if resp.status != 200 or cash_future.done():
                return
            try:
                body = await resp.json()
            except Exception:
                return
            v = _scan_for_cash(body)
            if v is not None:
                cash_future.set_result(v)

        page.on("response", on_response)
        try:
            await page.goto(BALANCE_PAGE, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:
            logger.warning("Groww: nav to balance page warning: %s", e)
        try:
            cash = await asyncio.wait_for(cash_future, timeout=timeout_seconds)
        except TimeoutError as e:
            raise RuntimeError(
                f"Groww: balance response not seen within {timeout_seconds:.0f}s "
                "— login may have expired or the dashboard layout changed."
            ) from e
        page.remove_listener("response", on_response)
        return cash
    finally:
        try:
            if page is not None:
                await page.close()
        finally:
            await browser.close()
            await pw.stop()
