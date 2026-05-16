"""INDmoney — capture free USD cash via CDP from the US-stocks holdings page.

The dashboard fires `/us-stocks-ext/api/v3/stocks/dw/user/account/basic` when
the holdings page loads. The response carries `cash_available_for_trade`
(USD), which is what the UI shows as "Wallet Balance: $X.XX".
"""

from __future__ import annotations

import asyncio
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome
from app.modules.brokers.broker_urls import (
    INDMONEY_BALANCE_PAGE as BALANCE_PAGE,
    INDMONEY_BALANCE_URL_NEEDLE as _NEEDLE,
)

logger = get_logger("brokers.indmoney_cash")


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _pick_cash(payload: Any) -> float | None:
    if not isinstance(payload, dict):
        return None
    for k in ("cash_available_for_trade", "balance_available"):
        if k in payload:
            return _to_float(payload[k])
    return None


async def capture_indmoney_cash(timeout_seconds: float = 25.0) -> float:
    """Open a fresh INDmoney tab, capture `/account/basic`, return USD cash."""
    pw, browser = await connect_existing_chrome()
    fut: asyncio.Future[float] = asyncio.get_event_loop().create_future()
    page = None
    try:
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await ctx.new_page()

        async def on_response(resp: Any) -> None:
            if _NEEDLE not in resp.url or resp.status != 200 or fut.done():
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
            await page.goto(BALANCE_PAGE, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:  # noqa: BLE001
            logger.warning("INDmoney: nav to balance page warning: %s", e)
        try:
            cash = await asyncio.wait_for(fut, timeout=timeout_seconds)
        except TimeoutError as e:
            raise RuntimeError(
                f"INDmoney: /account/basic not seen within {timeout_seconds:.0f}s "
                "— login may have expired or the URL needle changed."
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
