"""Attach to existing CDP Chrome, intercept Groww holdings-page XHRs.

Run while the Groww holdings page is open in the AlphaForge Anton Chrome:
    just groww-probe
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page

HOLDINGS_PAGE = "https://groww.in/stocks/user/holdings"
NEEDLES = ("holding", "portfolio", "tr_live", "stocks-portfolio", "user/holdings")


async def main() -> None:
    pw, browser = await connect_existing_chrome()
    page = await find_or_open_page(browser, HOLDINGS_PAGE, "groww.in")

    captured: list[dict] = []

    async def on_response(resp):  # noqa: ANN001
        url = resp.url
        if "groww.in" not in url:
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
            body_preview: object
            full_body: object = None
            if "application/json" in ct:
                try:
                    body = await resp.json()
                    body_preview = _shape_summary(body)
                    if "tr_live" in url or "latest_aggregated" in url:
                        full_body = body
                    # Diagnose ltp vs currentValue in holdings rows
                    if any(n in url for n in ("holding", "user/holdings")):
                        rows: object = body
                        if isinstance(body, dict):
                            for k in ("payload", "data", "holdings", "holdingsList"):
                                if isinstance(body.get(k), list):
                                    rows = body[k]
                                    break
                        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
                            s = rows[0]
                            body_preview = {
                                **(body_preview if isinstance(body_preview, dict) else {"summary": body_preview}),
                                "_diag": {
                                    "ltp": s.get("ltp"),
                                    "currentValue": s.get("currentValue"),
                                    "holdingValue": s.get("holdingValue"),
                                    "holdingAvgPrice": s.get("holdingAvgPrice"),
                                    "holdingQty": s.get("holdingQty"),
                                },
                            }
                except Exception as e:  # noqa: BLE001
                    body_preview = f"<json parse failed: {e}>"
            else:
                txt = await resp.text()
                body_preview = f"<{ct or 'no-ct'}, {len(txt)} chars>"
            entry = {
                "status": resp.status,
                "method": req.method,
                "url": url,
                "request_body": req_body,
                "shape": body_preview,
            }
            if full_body is not None:
                entry["full_body"] = full_body
            captured.append(entry)
        except Exception as e:  # noqa: BLE001
            captured.append({"status": resp.status, "url": url, "error": str(e)})

    page.on("response", on_response)

    print(f"Reloading {page.url} to capture XHRs...")
    try:
        await page.reload(wait_until="networkidle", timeout=30000)
    except Exception as e:  # noqa: BLE001
        print(f"reload warning: {e}")

    await asyncio.sleep(3)

    print(f"\nCaptured {len(captured)} candidate requests:\n")
    for c in captured:
        print(json.dumps(c, indent=2, default=str))
        print("-" * 60)

    await browser.close()
    await pw.stop()


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
