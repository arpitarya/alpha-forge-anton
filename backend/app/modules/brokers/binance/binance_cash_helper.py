"""Binance — capture free USD/USDT cash via CDP from the wallet page.

Sums the spot wallet's free fiatValuation across the USDT/USDC/BUSD rows
captured from the wallet/balance XHR. Probe-confirm the needle and field
shape with `probes/binance_cash_probe.py` before trusting.
"""

from __future__ import annotations

import asyncio
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome
from app.modules.brokers.broker_urls import (
    BINANCE_BALANCE_PAGE as BALANCE_PAGE,
    BINANCE_BALANCE_URL_NEEDLES as _NEEDLES,
)

logger = get_logger("brokers.binance_cash")
_STABLE = {"USDT", "USDC", "BUSD", "FDUSD", "USD"}


def _f(v: Any) -> float:
    if v in (None, ""):
        return 0.0
    if isinstance(v, str):
        v = v.replace(",", "").strip()
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _pick_cash(payload: Any) -> float | None:
    """Sum free balances of stablecoins from a Binance wallet payload."""
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    rows: list[dict[str, Any]] = []
    if isinstance(data, list):
        rows = [r for r in data if isinstance(r, dict)]
    elif isinstance(data, dict):
        for k in ("assets", "list", "balances"):
            v = data.get(k)
            if isinstance(v, list):
                rows = [r for r in v if isinstance(r, dict)]; break
        if not rows:
            for k in ("totalAssetOfBtc", "fiatBalance", "usdAmount"):
                if k in data:
                    return _f(data[k])
    cash = sum(
        (_f(r.get("free")) or _f(r.get("fiatValuation")))
        for r in rows
        if str(r.get("asset") or r.get("coin") or "").upper() in _STABLE
    )
    return cash if cash else None


async def capture_binance_cash(timeout_seconds: float = 25.0) -> float:
    """Open a fresh Binance tab, capture wallet/balance, return USD cash."""
    pw, browser = await connect_existing_chrome()
    fut: asyncio.Future[float] = asyncio.get_event_loop().create_future()
    page = None
    try:
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await ctx.new_page()

        async def on_response(resp: Any) -> None:
            if not any(n in resp.url for n in _NEEDLES) or resp.status != 200 or fut.done():
                return
            try:
                body = await resp.json()
            except Exception:  # noqa: BLE001
                return
            v = _pick_cash(body)
            if v is not None: fut.set_result(v)

        page.on("response", on_response)
        try:
            await page.goto(BALANCE_PAGE, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:  # noqa: BLE001
            logger.warning("Binance: nav to balance page warning: %s", e)
        try:
            cash = await asyncio.wait_for(fut, timeout=timeout_seconds)
        except TimeoutError as e:
            raise RuntimeError(
                f"Binance: wallet/balance not seen within {timeout_seconds:.0f}s "
                "— login expired or needles changed (probes/binance_cash_probe.py)."
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
