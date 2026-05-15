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

logger = get_logger("brokers.groww_cash")

BALANCE_PAGE = "https://groww.in/v2/balance"

# Substrings that mark a balance/wallet API response. Groww doesn't keep a
# single canonical endpoint — the dashboard hits several, any one of which
# carries the available-cash figure.
_BALANCE_URL_NEEDLES = (
    "/api/user/v1/balance",
    "/api/users/v1/balance",
    "/api/user/v2/balance",
    "/v1/api/user/balance",
    "/userbalance/v1",
    "/wallet/v1",
)
_CASH_KEYS = (
    "availableMargin", "availableBalance", "availableCash", "cashAvailable",
    "freeCash", "totalAvailableBalance", "withdrawableCash", "walletBalance",
    "currentBalance",
)


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _scan_for_cash(node: Any) -> float | None:
    """DFS through arbitrary JSON, returning the first cash-shaped value found."""
    stack: list[Any] = [node]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k in _CASH_KEYS:
                if k in cur and isinstance(cur[k], (int, float, str)):
                    val = _to_float(cur[k])
                    if val:
                        return val
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
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
