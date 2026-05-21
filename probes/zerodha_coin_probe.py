"""Attach to existing CDP Chrome, read Zerodha enctoken, probe Coin MF API.

Run while logged in to kite.zerodha.com in the AlphaForge Anton Chrome:
    uv run python probes/zerodha_coin_probe.py

Coins MF holdings live at /api/mf/holdings on the Kite OMS — same enctoken
as the equity API. This probe confirms the endpoint is reachable and prints
the field path (data[].tradingsymbol, quantity, average_price, last_price,
pnl) so `zerodha_coin_source.py` can be audited against live data.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import httpx

from app.modules.brokers._cdp import connect_existing_chrome, cookie_value, find_or_open_page

KITE_BASE = "https://kite.zerodha.com"
LOGIN_URL = "https://kite.zerodha.com/"
COIN_MF_HOLDINGS = "/oms/mf/holdings"


async def _acquire_enctoken() -> str | None:
    pw, browser = await connect_existing_chrome()
    try:
        page = await find_or_open_page(browser, LOGIN_URL, "kite.zerodha.com")
        token = await cookie_value(page.context, "enctoken", "kite.zerodha.com")
        if not token:
            print("No enctoken cookie found — log in to kite.zerodha.com in Chrome first.")
        return token
    finally:
        await browser.close()
        await pw.stop()


def _shape_summary(body: object) -> object:
    if isinstance(body, list):
        sample = body[0] if body and isinstance(body[0], dict) else None
        return {
            "type": "list", "len": len(body),
            "sample_keys": sorted(sample.keys()) if sample else None,
            "sample": sample,
        }
    if isinstance(body, dict):
        out: dict = {"type": "dict", "keys": sorted(body.keys())}
        for k, v in body.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                out["list_at"] = k
                out["list_len"] = len(v)
                out["list_sample_keys"] = sorted(v[0].keys())
                # Field path audit — critical for zerodha_coin_source_helper.py
                print(f"\n  Field path: data[].{k}[0] keys → {sorted(v[0].keys())}")
                print(f"  Sample row: {json.dumps(v[0], default=str)[:400]}")
                return out
        return out
    return {"type": type(body).__name__, "preview": str(body)[:200]}


async def main() -> None:
    enctoken = await _acquire_enctoken()
    if not enctoken:
        return

    print(f"enctoken: {enctoken[:12]}...{enctoken[-4:]} (truncated)\n")
    headers = {"Authorization": f"enctoken {enctoken}", "X-Kite-Version": "3"}

    async with httpx.AsyncClient(base_url=KITE_BASE, headers=headers, timeout=15.0) as client:
        client.cookies.set("enctoken", enctoken, domain="kite.zerodha.com")
        try:
            resp = await client.get(COIN_MF_HOLDINGS)
            print(f"── GET {COIN_MF_HOLDINGS}  [{resp.status_code}]")
            if "json" in resp.headers.get("content-type", ""):
                body = resp.json()
                print(json.dumps(_shape_summary(body), indent=2, default=str))
                # Print the full data for field-path audit
                data = body.get("data") if isinstance(body, dict) else body
                if isinstance(data, list) and data:
                    print(f"\nFirst MF row (full):\n{json.dumps(data[0], indent=2, default=str)}")
                    print(f"\nTotal MF holdings: {len(data)}")
            else:
                print(resp.text[:400])
        except Exception as e:  # noqa: BLE001
            print(f"Error probing {COIN_MF_HOLDINGS}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
