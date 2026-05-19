"""Attach to existing CDP Chrome, intercept INDmoney portfolio XHRs.

Run while logged in to indmoney.com in the AlphaForge Anton Chrome:
    uv run python probes/indmoney_probe.py

Prints a shape summary of every matching XHR. Look for a response that lists
holdings (quantity / avg_price / ltp / isin) — that is the payload that drives
`_HOLDINGS_URL_NEEDLE` and `normalize()` in indmoney_source_helper.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page

HOLDINGS_PAGE = "https://www.indmoney.com/dashboard"
NEEDLES = (
    "holding", "portfolio", "position", "asset", "instrument",
    "stocks", "mutual", "us-stocks", "gold", "investment",
)


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


async def _capture(page, label: str) -> list[dict]:
    captured: list[dict] = []

    async def on_response(resp) -> None:  # noqa: ANN001
        url = resp.url
        if "indmoney" not in url:
            return
        if not any(n in url.lower() for n in NEEDLES):
            return
        try:
            req = resp.request
            req_body = None
            if req.method in ("POST", "PUT", "PATCH"):
                try:
                    raw = req.post_data
                    req_body = json.loads(raw) if raw else None
                except Exception:  # noqa: BLE001
                    req_body = req.post_data
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
                "page": label,
                "status": resp.status,
                "method": req.method,
                "url": url,
                "request_body": req_body,
                "shape": body_preview,
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
        page = await find_or_open_page(browser, HOLDINGS_PAGE, "indmoney")
        if "login" in page.url.lower():
            print("Not logged in — please log in to indmoney.com in Chrome first.")
            return
        captured = await _capture(page, "dashboard")
        print(f"\n{'=' * 60}\nCaptured {len(captured)} candidate requests:\n{'=' * 60}\n")
        for c in captured:
            print(json.dumps(c, indent=2, default=str))
            print("-" * 60)
        if not captured:
            print(
                "Nothing captured. The dashboard may load holdings via scroll/click; "
                "interact with the page (navigate to Stocks / Mutual Funds / US Stocks "
                "tabs) and re-run, or broaden NEEDLES."
            )
    finally:
        await browser.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
