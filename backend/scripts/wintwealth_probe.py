"""Attach to existing CDP Chrome, intercept Wint Wealth portfolio-page XHRs.

Run while logged in to wintwealth.com in the AlphaForge Chrome:
    cd backend && uv run python scripts/wintwealth_probe.py

Prints a shape summary of every matching XHR. Look for a response with
`isin`, `units`, `currentPrice`, or `securityName` — that is the holdings
payload that drives `_NEEDLES` and `normalize()` in wintwealth_source_helper.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page

# Probe-confirmed: the holdings XHR fires on the /portfolio/bonds/ page.
# api.wintwealth.com/investments/v2?userId=...&investmentType=CURRENT&productType=BOND
PORTFOLIO_PAGE = "https://www.wintwealth.com/portfolio/bonds/"
NEEDLES = (
    "investments",
    "portfolio",
    "holdings",
    "transaction",
    "bond",
    "dashboard",
)


async def main() -> None:
    pw, browser = await connect_existing_chrome()
    page = await find_or_open_page(browser, PORTFOLIO_PAGE, "wintwealth.com")

    if "/login" in page.url or "sign" in page.url.lower():
        print("Not logged in — please log in to wintwealth.com in Chrome first.")
        await browser.close()
        await pw.stop()
        return

    if "/portfolio" not in page.url and "/investment" not in page.url:
        print(f"Navigating to {PORTFOLIO_PAGE}...")
        try:
            await page.goto(PORTFOLIO_PAGE, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:  # noqa: BLE001
            print(f"nav warning: {e}")

    captured: list[dict] = []

    async def on_response(resp) -> None:  # noqa: ANN001
        url = resp.url
        if "wintwealth.com" not in url:
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
                "status": resp.status,
                "method": req.method,
                "url": url,
                "request_body": req_body,
                "shape": body_preview,
            })
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

    if not captured:
        print(
            "Nothing captured — the page may require interaction to trigger the XHR.\n"
            "Try scrolling or clicking on the portfolio tab, then re-run."
        )

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
