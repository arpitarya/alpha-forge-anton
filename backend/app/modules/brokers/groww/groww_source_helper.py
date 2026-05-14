"""Groww — CDP login + holdings fetch via the authenticated browser context.

Approach: Groww's API requires a per-request `x-request-checksum` (an HMAC
computed by their client-side JS) plus a JWT bearer token. Replicating that
from outside the page is infeasible. Instead we attach to the running Chrome,
register a response listener for the holdings endpoint, then reload the page
so Groww's own JS makes the call with all interceptors wired up. We just
read the response off the wire.

Login flow: user logs in to groww.in inside Chrome (started with
--remote-debugging-port=9299).
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page

logger = get_logger("brokers.groww_helper")

HOLDINGS_PAGE = "https://groww.in/stocks/user/holdings"
LOGIN_URL = "https://groww.in/login"
REQUIRED_ENV: tuple[str, ...] = ("GROWW_USER_ID",)

_CDP_WAIT_SECONDS = int(os.getenv("GROWW_LOGIN_CDP_WAIT", "180"))


def env(key: str) -> str:
    return os.getenv(key, "").strip()


async def _ensure_logged_in(page: Any, wait_seconds: int) -> None:
    """If the page is on /login, wait for the user to complete login."""
    if "/login" not in page.url:
        return
    logger.info("Groww: waiting up to %ss for manual login in attached Chrome", wait_seconds)
    await page.wait_for_url(
        lambda url: "/login" not in url and "groww.in" in url,
        timeout=wait_seconds * 1000,
    )


def _looks_like_holding(row: Any) -> bool:
    if not isinstance(row, dict):
        return False
    keys = set(row)
    if keys & {
        "tradingSymbol",
        "symbol",
        "nseScriptCode",
        "scripCode",
        "isin",
        "isinCode",
        "quantity",
        "totalQuantity",
        "holdingQuantity",
        "holdingQty",
        "netQty",
    }:
        return True
    # New /v2 shape nests identifiers under symbolData.
    sd = row.get("symbolData")
    return isinstance(sd, dict) and bool(
        set(sd) & {"tradingSymbol", "scripCode", "nseScripCode", "symbolIsin"}
    )


def _extract_holdings_list(payload: Any) -> list[dict[str, Any]]:
    """Drill into common Groww response shapes to find the holdings list."""
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    candidates = (
        ("payload", "holdings"),
        ("payload", "holdingsList"),
        ("payload", "data", "holdings"),
        ("payload", "data", "holdingsList"),
        ("data", "holdings"),
        ("data", "holdingsList"),
        ("data", "stockHoldings"),
        ("data", "portfolio", "holdings"),
        ("data",),
        ("holdings",),
        ("holdingsList",),
        ("stockHoldings",),
        ("payload",),
    )
    for path in candidates:
        node: Any = payload
        for key in path:
            if not isinstance(node, dict) or key not in node:
                node = None
                break
            node = node[key]
        if isinstance(node, list) and any(_looks_like_holding(row) for row in node):
            return [row for row in node if isinstance(row, dict)]

    stack = [payload]
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            if any(_looks_like_holding(row) for row in node):
                return [row for row in node if isinstance(row, dict)]
            stack.extend(node)
        elif isinstance(node, dict):
            stack.extend(node.values())
    return []


def _pick(row: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """First non-None value across `keys` — handles camelCase/snake_case drift."""
    for k in keys:
        v = row.get(k)
        if v not in (None, ""):
            return v
    return default


# Groww V2 holdings API returns prices/values in paise (1/100 INR).
# tr_live (/tr_live/segment/...) returns rupees. Mixing the two yields ~100× errors.
_PAISE_FIELDS = frozenset({
    "holdingAvgPrice", "ltp", "currentValue", "holdingValue",
    "totalCurrentValue", "currentHoldingValue", "unrealisedHoldingValue", "currentWorth",
})


def _price_field(row: dict[str, Any], *keys: str) -> float:
    """Return first non-empty value from `keys` in **rupees**, scaling paise fields by 1/100."""
    for k in keys:
        v = row.get(k)
        if v in (None, ""):
            continue
        f = _to_float(v)
        return f / 100.0 if k in _PAISE_FIELDS else f
    return 0.0


def normalize(row: dict[str, Any]) -> dict[str, Any]:
    """Map a Groww holdings row to the shared dict shape used by dump.py."""
    sd = row.get("symbolData") if isinstance(row.get("symbolData"), dict) else {}
    qty = _to_float(
        _pick(row, "holdingQty", "netQty", "quantity", "totalQuantity", "holdingQuantity")
    )
    avg = _price_field(
        row, "holdingAvgPrice", "netPrice", "averagePrice", "avgPrice", "buyPrice"
    )
    ltp = _price_field(row, "ltp", "lastTradedPrice", "currentPrice", "nav")
    # Groww's holdings API usually returns ltp=0; derive from total current value instead.
    if not ltp and qty:
        total_cur = _price_field(
            row, "currentValue", "holdingValue", "totalCurrentValue",
            "currentHoldingValue", "unrealisedHoldingValue", "currentWorth",
        )
        if total_cur:
            ltp = total_cur / qty
    name = _pick(
        sd, "companyShortName", "companyName", "displayName", "symbolName", "shortName"
    ) or _pick(row, "companyShortName", "companyName", "displayName", "name")
    return {
        "tradingsymbol": str(
            _pick(
                sd, "tradingSymbol", "nseTradingSymbol", "scripCode", "nseScripCode"
            )
            or _pick(row, "tradingSymbol", "symbol", "nseScriptCode", "scripCode")
            or ""
        ).upper(),
        "name": str(name).strip() if name else "",
        "isin": _pick(sd, "symbolIsin") or _pick(row, "isin", "isinCode") or "",
        "exchange": _pick(sd, "exchange") or _pick(row, "exchange", "exchangeName") or "NSE",
        "quantity": qty,
        "average_price": avg,
        "last_price": ltp,
    }


def _to_float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


_HOLDINGS_URL_NEEDLES = ("/v2/api/stocks/holdings/all", "/user/holdings")
_LTP_URL_NEEDLE = "/tr_live/segment/CASH/latest_aggregated"


async def _capture_holdings_via_reload(
    page: Any, timeout_seconds: float = 25.0
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    """Reload the holdings page and capture the holdings + LTP responses.

    Groww's API needs an HMAC checksum header that only their client JS knows
    how to compute. So we just listen to the responses Groww's own page makes.
    """
    holdings_future: asyncio.Future[list[dict[str, Any]]] = asyncio.get_event_loop().create_future()
    ltps: dict[str, float] = {}

    async def on_response(resp: Any) -> None:
        url = resp.url
        try:
            if any(n in url for n in _HOLDINGS_URL_NEEDLES) and not holdings_future.done():
                if resp.status != 200:
                    return
                body = await resp.json()
                rows = _extract_holdings_list(body)
                if rows:
                    holdings_future.set_result(rows)
            elif _LTP_URL_NEEDLE in url and resp.status == 200:
                body = await resp.json()
                _merge_ltps(body, ltps)
        except Exception as e:  # noqa: BLE001
            logger.debug("Groww: response handler skipped %s: %s", url, e)

    page.on("response", on_response)
    try:
        try:
            await page.reload(wait_until="domcontentloaded", timeout=20000)
        except Exception as e:  # noqa: BLE001
            logger.warning("Groww: page.reload warning: %s — continuing to wait for XHR", e)
        try:
            holdings = await asyncio.wait_for(holdings_future, timeout=timeout_seconds)
        except TimeoutError as e:
            raise RuntimeError(
                "Groww: holdings response did not arrive within "
                f"{timeout_seconds:.0f}s after reload. Login may have expired."
            ) from e
        # Give the LTP call a brief grace window — it fires after holdings.
        await asyncio.sleep(2.5)
    finally:
        page.remove_listener("response", on_response)
    return holdings, ltps


def _merge_ltps(body: Any, out: dict[str, float]) -> None:
    if not isinstance(body, dict):
        return
    # Primary shape: exchangeAggRespMap.EXCHANGE.priceLivePointsMap.SYM.{value|ltp|close}
    agg = body.get("exchangeAggRespMap") or {}
    for exch_payload in agg.values():
        if not isinstance(exch_payload, dict):
            continue
        prices = exch_payload.get("priceLivePointsMap") or {}
        for sym, point in prices.items():
            if isinstance(point, dict):
                v = point.get("value") or point.get("ltp") or point.get("close")
                if v is not None:
                    out[str(sym).upper()] = float(v)
    # Fallback: flat SYM→price map nested under common top-level keys
    for top_key in ("data", "payload", "liveData", "priceData", "prices"):
        flat = body.get(top_key)
        if not isinstance(flat, dict):
            continue
        for sym, val in flat.items():
            if isinstance(val, (int, float)):
                out[str(sym).upper()] = float(val)
            elif isinstance(val, dict):
                v = val.get("value") or val.get("ltp") or val.get("close") or val.get("price")
                if v is not None:
                    out[str(sym).upper()] = float(v)


async def fetch_holdings_via_browser(*, force_login: bool = False) -> list[dict[str, Any]]:
    """Attach to Chrome, reload Groww's holdings page, capture the response."""
    pw, browser = await connect_existing_chrome()
    try:
        target = LOGIN_URL if force_login else HOLDINGS_PAGE
        page = await find_or_open_page(browser, target, "groww.in")
        await _ensure_logged_in(page, _CDP_WAIT_SECONDS)

        # Always navigate to the holdings page — guarantees the XHR fires on reload.
        if "/stocks/user/holdings" not in page.url:
            try:
                await page.goto(HOLDINGS_PAGE, wait_until="domcontentloaded", timeout=20000)
            except Exception as e:  # noqa: BLE001
                logger.warning("Groww: nav to holdings page failed (%s); proceeding anyway", e)

        raw_holdings, ltps = await _capture_holdings_via_reload(page)
        logger.info(
            "Groww: captured %d holdings + %d LTPs via page reload",
            len(raw_holdings), len(ltps),
        )

        normalized: list[dict[str, Any]] = []
        for h in raw_holdings:
            row = normalize(h)
            if not row["last_price"]:
                sym = row["tradingsymbol"].split("-")[0]
                row["last_price"] = ltps.get(sym) or row["average_price"]
            normalized.append(row)
        if not ltps:
            logger.info(
                "Groww: no LTP payload captured — using avg_price as last_price (PnL=0)"
            )
        return normalized
    finally:
        await browser.close()
        await pw.stop()
