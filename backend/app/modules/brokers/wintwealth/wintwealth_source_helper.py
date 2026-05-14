"""Wint Wealth — CDP browser fetch (no public API).

Probe-confirmed endpoint: api.wintwealth.com/investments/v2?productType=BOND
fires when the /portfolio/bonds/ page reloads. Field names are real API names
from wintwealth_probe.py output (productName, scripCode, totalQuantity, etc.).
Log in to wintwealth.com in Chrome (--remote-debugging-port=9299) first.
"""
from __future__ import annotations

import asyncio, os
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page

logger = get_logger("brokers.wintwealth_helper")
BONDS_PAGE = "https://www.wintwealth.com/portfolio/bonds/"
LOGIN_URL  = "https://www.wintwealth.com/login"
REQUIRED_ENV: tuple[str, ...] = ("WINTWEALTH_USER_ID",)
_WAIT = int(os.getenv("WINTWEALTH_LOGIN_CDP_WAIT", "180"))
_INVESTMENTS_API = "api.wintwealth.com/investments/v2"


def env(key: str) -> str:
    return os.getenv(key, "").strip()


def _to_float(v: Any) -> float:
    try:
        return float(str(v).replace(",", "").replace("₹", "").strip())
    except (TypeError, ValueError):
        return 0.0


def normalize(row: dict[str, Any]) -> dict[str, Any]:
    isin  = str(row.get("isin") or "")
    name  = str(row.get("productName") or row.get("name") or "")
    sym   = str(row.get("scripCode") or isin or name[:24].upper().replace(" ", "_"))
    qty   = _to_float(row.get("totalQuantity") or row.get("quantity"))
    total_inv = _to_float(row.get("investment") or row.get("investedAmount"))
    total_cur = _to_float(row.get("currentValue") or row.get("currentAmount"))
    avg   = (total_inv / qty) if qty else _to_float(row.get("issuePrice"))
    ltp   = (total_cur / qty) if qty else avg
    atype = str(row.get("productType") or row.get("assetType") or "BOND").upper()
    return {"tradingsymbol": sym.upper(), "isin": isin, "name": name,
            "exchange": str(row.get("exchange") or "NSE"), "quantity": qty,
            "average_price": avg, "last_price": ltp,
            "asset_type": "gold" if any(k in atype for k in ("SGB", "GOLD")) else "bond"}

def _extract(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    for path in (("investments",), ("data", "investments"), ("data",), ("holdings",), ("payload",)):
        node: Any = payload
        for k in path:
            node = node.get(k) if isinstance(node, dict) else None
        if isinstance(node, list) and node and isinstance(node[0], dict):
            return node
    return []


async def fetch_holdings_via_browser(*, force_login: bool = False) -> list[dict[str, Any]]:
    pw, browser = await connect_existing_chrome()
    try:
        page = await find_or_open_page(browser, LOGIN_URL if force_login else BONDS_PAGE, "wintwealth.com")
        if "/login" in page.url or "sign" in page.url.lower():
            logger.info("WintWealth: waiting up to %ss for manual login", _WAIT)
            await page.wait_for_url(lambda u: "/login" not in u and "wintwealth.com" in u, timeout=_WAIT * 1000)
        if "/portfolio/bonds" not in page.url:
            try:
                await page.goto(BONDS_PAGE, wait_until="domcontentloaded", timeout=20000)
            except Exception as e:  # noqa: BLE001
                logger.warning("WintWealth: nav to bonds page failed (%s); proceeding", e)

        collected: list[list[dict[str, Any]]] = []
        async def on_response(resp: Any) -> None:
            if _INVESTMENTS_API in resp.url and resp.status == 200:
                try:
                    rows = _extract(await resp.json())
                    if rows:
                        collected.append(rows)
                except Exception as e:  # noqa: BLE001
                    logger.debug("WintWealth: response parse error: %s", e)
        page.on("response", on_response)
        try:
            try:
                await page.reload(wait_until="domcontentloaded", timeout=20000)
            except Exception as e:  # noqa: BLE001
                logger.warning("WintWealth: reload warning: %s", e)
            await asyncio.sleep(5.0)  # allow all productType calls to complete
        finally:
            page.remove_listener("response", on_response)

        if not collected:
            raise RuntimeError(
                "WintWealth: no data from investments/v2 after reload — login may have expired."
            )
        all_rows = [r for batch in collected for r in batch]
        normalized = [normalize(r) for r in all_rows]
        logger.info("WintWealth: captured %d holdings (%d batch(es))", len(normalized), len(collected))
        return normalized
    finally:
        await browser.close()
        await pw.stop()
