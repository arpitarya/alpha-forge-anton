"""Angel One — capture free-cash balance via CDP from the funds page.

Probe-confirmed endpoint:
    POST https://amx-*.angelone.in/funds/v2/getRMSLimit
    body {exchange, product, segment} → data.netAvailableFunds (₹)

Open the funds dashboard in a fresh tab, listen for the getRMSLimit XHR, then
close the tab so it doesn't linger in the user's Chrome.
"""

from __future__ import annotations

import asyncio
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome

logger = get_logger("brokers.angelone_cash")

FUNDS_PAGE = "https://www.angelone.in/trade/funds"

_RMS_URL_NEEDLE = "/funds/v2/getRMSLimit"
# Priority order: netAvailableFunds is the canonical "what you can actually
# withdraw / use to place a new order". fundsForTrading and fundsAvailable are
# fallbacks for older API shapes.
_CASH_KEYS: tuple[str, ...] = (
    "netAvailableFunds",
    "fundsForTrading",
    "fundsAvailable",
    "fundsForAllocation",
)


def _to_float(v: Any) -> float:
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


def _pick_cash(payload: Any) -> float | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, dict):
        return None
    for k in _CASH_KEYS:
        if k in data:
            return _to_float(data[k])
    return None


async def capture_angelone_cash(timeout_seconds: float = 25.0) -> float:
    pw, browser = await connect_existing_chrome()
    fut: asyncio.Future[float] = asyncio.get_event_loop().create_future()
    page = None
    try:
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await ctx.new_page()

        async def on_response(resp: Any) -> None:
            if _RMS_URL_NEEDLE not in resp.url:
                return
            if resp.status != 200 or fut.done():
                return
            try:
                body = await resp.json()
            except Exception:  # noqa: BLE001
                return
            v = _pick_cash(body)
            if v is not None:
                fut.set_result(v)

        page.on("response", on_response)
        try:
            await page.goto(FUNDS_PAGE, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:  # noqa: BLE001
            logger.warning("Angel One: nav to funds page warning: %s", e)
        try:
            cash = await asyncio.wait_for(fut, timeout=timeout_seconds)
        except TimeoutError as e:
            raise RuntimeError(
                f"Angel One: getRMSLimit response not seen within {timeout_seconds:.0f}s "
                "— login may have expired or the funds page changed."
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
