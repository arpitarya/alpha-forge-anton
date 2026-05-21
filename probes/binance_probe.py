"""Attach to existing CDP Chrome, intercept Binance wallet XHRs.

Run while logged in to binance.com in the AlphaForge Anton Chrome:
    uv run python probes/binance_probe.py

Prints a shape summary of every matching XHR. Look for a response that lists
spot wallet assets (asset / free / locked / fiatValuation) — that is the payload
that drives `BINANCE_HOLDINGS_URL_NEEDLES` and `normalize()` in
binance_source_helper.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page

HOLDINGS_PAGE = "https://www.binance.com/en/my/wallet/account/main"
NEEDLES = (
    "wallet", "asset-service", "balance", "spot", "holding",
    "portfolio", "user-asset", "capital",
)


def _shape_summary(body: object) -> object:
    if isinstance(body, list):
        return {
            "type": "list", "len": len(body),
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


async def _capture(page, label: str) -> list[dict]:
    captured: list[dict] = []

    async def on_response(resp) -> None:  # noqa: ANN001
        url = resp.url
        if "binance.com" not in url:
            return
        if not any(n in url.lower() for n in NEEDLES):
            return
        try:
            ct = (resp.headers.get("content-type") or "").lower()
            if "application/json" in ct:
                try:
                    body = await resp.json()
                    body_preview = _shape_summary(body)
                except Exception as e:  # noqa: BLE001
                    body_preview = f"<json parse failed: {e}>"
            else:
                txt = await resp.text()
                body_preview = f"<{ct or 'no-ct'}, {len(txt)} chars>"
            captured.append({
                "page": label, "status": resp.status, "method": resp.request.method,
                "url": url, "shape": body_preview,
            })
        except Exception as e:  # noqa: BLE001
            captured.append({"page": label, "status": resp.status, "url": url, "error": str(e)})

    page.on("response", on_response)
    print(f"[{label}] reloading {page.url} to capture XHRs...")
    try:
        await page.reload(wait_until="networkidle", timeout=30000)
    except Exception as e:  # noqa: BLE001
        print(f"[{label}] reload warning: {e}")
    await asyncio.sleep(5)
    page.remove_listener("response", on_response)
    return captured


async def main() -> None:
    pw, browser = await connect_existing_chrome()
    try:
        page = await find_or_open_page(browser, HOLDINGS_PAGE, "binance")
        if "login" in page.url.lower() or "accounts.binance.com" in page.url.lower():
            print("Not logged in — please log in to binance.com in Chrome first.")
            return
        captured = await _capture(page, "wallet")
        print(f"\n{'=' * 60}\nCaptured {len(captured)} candidate requests:\n{'=' * 60}\n")
        for c in captured:
            print(json.dumps(c, indent=2, default=str))
            print("-" * 60)
        if not captured:
            print("Nothing captured — broaden NEEDLES or check login state.")
    finally:
        await browser.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
