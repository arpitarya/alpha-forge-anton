"""Attach to existing CDP Chrome, read Zerodha enctoken, probe Kite OMS API.

Run while logged in to kite.zerodha.com in the AlphaForge Chrome:
    cd backend && uv run python scripts/zerodha_probe.py

Unlike the Groww/Wint Wealth probes (XHR interception), Zerodha has a
documented REST API. This probe reads the enctoken from the live Chrome
session and fires direct API calls so you can inspect the live response shape
for holdings, positions, margins, and profile.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

from app.modules.brokers._cdp import connect_existing_chrome, cookie_value, find_or_open_page

KITE_BASE = "https://kite.zerodha.com"
LOGIN_URL  = "https://kite.zerodha.com/"

ENDPOINTS = [
    ("GET", "/oms/portfolio/holdings"),
    ("GET", "/oms/portfolio/positions"),
    ("GET", "/oms/user/profile"),
    ("GET", "/oms/user/margins"),
]


async def _acquire_enctoken() -> str | None:
    """Read the enctoken cookie from the attached Chrome session."""
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


async def _probe(client: httpx.AsyncClient, method: str, path: str) -> dict:
    try:
        resp = await client.request(method, path)
        if "json" in resp.headers.get("content-type", ""):
            try:
                return {"status": resp.status_code, "path": path, "shape": _shape_summary(resp.json())}
            except Exception as e:  # noqa: BLE001
                return {"status": resp.status_code, "path": path, "error": f"json parse: {e}"}
        return {"status": resp.status_code, "path": path, "body_preview": resp.text[:200]}
    except Exception as e:  # noqa: BLE001
        return {"path": path, "error": str(e)}


async def main() -> None:
    enctoken = await _acquire_enctoken()
    if not enctoken:
        return

    print(f"enctoken: {enctoken[:12]}...{enctoken[-4:]} (truncated)\n")
    headers = {"Authorization": f"enctoken {enctoken}", "X-Kite-Version": "3"}

    async with httpx.AsyncClient(base_url=KITE_BASE, headers=headers, timeout=15.0) as client:
        client.cookies.set("enctoken", enctoken, domain="kite.zerodha.com")
        for method, path in ENDPOINTS:
            result = await _probe(client, method, path)
            print(f"── {method} {path}")
            print(json.dumps(result, indent=2, default=str))
            print("-" * 60)


def _shape_summary(body: object) -> object:
    """Compact preview: top-level keys + first list-of-dict path with sample."""
    if isinstance(body, list):
        return {
            "type": "list",
            "len": len(body),
            "sample_keys": sorted(body[0].keys()) if body and isinstance(body[0], dict) else None,
            "sample": body[0] if body else None,
        }
    if isinstance(body, dict):
        out: dict = {"type": "dict", "keys": sorted(body.keys())}
        for k, v in body.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                out["first_list_at"] = k
                out["first_list_len"] = len(v)
                out["first_list_sample_keys"] = sorted(v[0].keys())
                out["first_list_sample"] = v[0]
                return out
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, list) and v2 and isinstance(v2[0], dict):
                        out["first_list_at"] = f"{k}.{k2}"
                        out["first_list_len"] = len(v2)
                        out["first_list_sample_keys"] = sorted(v2[0].keys())
                        out["first_list_sample"] = v2[0]
                        return out
        return out
    return {"type": type(body).__name__, "preview": str(body)[:200]}


if __name__ == "__main__":
    asyncio.run(main())
