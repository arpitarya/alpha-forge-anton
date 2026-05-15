"""Attach to existing CDP Chrome, intercept Gullak dashboard XHRs.

Run while logged in to web.gullak.money in the AlphaForge Chrome:
    just gullak-probe

Prints a shape summary of every matching XHR. Look for responses with
gold/silver holdings quantity, invested, currentValue — those fields
drive `_NEEDLES` and `normalize()` in gullak_source_helper.py.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome, find_or_open_page

DASHBOARD_PAGE = "https://web.gullak.money/dashboard"

# Injected before page load so it survives navigation
_INTERCEPT_SCRIPT = """
window.__gullakCaptured = [];

const _origFetch = window.fetch;
window.fetch = async function(...args) {
  const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
  const resp = await _origFetch(...args);
  if (url.includes('api.gullak') || url.includes('gullak.money')) {
    try {
      const clone = resp.clone();
      const text = await clone.text();
      window.__gullakCaptured.push({
        url,
        method: (args[1]?.method || 'GET'),
        status: resp.status,
        contentType: resp.headers.get('content-type') || '',
        body: text.substring(0, 5000),
      });
    } catch(e) {
      window.__gullakCaptured.push({ url, error: e.message });
    }
  }
  return resp;
};

// Also cover XMLHttpRequest
const _XHR = window.XMLHttpRequest;
window.XMLHttpRequest = function() {
  const xhr = new _XHR();
  const origOpen = xhr.open.bind(xhr);
  let _url = '';
  xhr.open = function(method, url, ...rest) {
    _url = url;
    return origOpen(method, url, ...rest);
  };
  xhr.addEventListener('load', function() {
    if (_url.includes('api.gullak') || _url.includes('gullak.money')) {
      window.__gullakCaptured.push({
        url: _url,
        method: 'XHR',
        status: xhr.status,
        contentType: xhr.getResponseHeader('content-type') || '',
        body: (xhr.responseText || '').substring(0, 5000),
      });
    }
  });
  return xhr;
};
"""


async def main() -> None:
    pw, browser = await connect_existing_chrome()
    page = await find_or_open_page(browser, DASHBOARD_PAGE, "gullak.money")

    if "/login" in page.url or "signin" in page.url.lower():
        print("Not logged in — please log in to web.gullak.money in Chrome first.")
        await browser.close()
        await pw.stop()
        return

    # Inject interceptor so it survives reload
    await page.add_init_script(_INTERCEPT_SCRIPT)

    print(f"Reloading {page.url} with fetch/XHR interceptor installed...")
    try:
        await page.reload(wait_until="networkidle", timeout=30000)
    except Exception as e:  # noqa: BLE001
        print(f"reload warning: {e}")

    await asyncio.sleep(4)

    captured: list[dict] = await page.evaluate("() => window.__gullakCaptured || []")

    print(f"\nCaptured {len(captured)} Gullak API calls:\n")
    for c in captured:
        url = c.get("url", "")
        body_str = c.get("body", "")
        try:
            body_json = json.loads(body_str)
            shape = _shape_summary(body_json)
            raw_preview = None
        except Exception:  # noqa: BLE001
            shape = f"<non-JSON {len(body_str)} chars>"
            raw_preview = repr(body_str[:300])
        entry = {
            "status": c.get("status"),
            "method": c.get("method"),
            "url": url,
            "contentType": c.get("contentType"),
            "shape": shape,
        }
        if raw_preview:
            entry["rawPreview"] = raw_preview
        print(json.dumps(entry, indent=2, default=str))
        print("-" * 60)

    if not captured:
        print(
            "Nothing captured.\n"
            "  1. Confirm you are logged in to web.gullak.money in Chrome.\n"
            "  2. Check that Chrome was started with --remote-debugging-port=9299.\n"
            "  3. Check the browser Network tab manually and widen the URL filter."
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
