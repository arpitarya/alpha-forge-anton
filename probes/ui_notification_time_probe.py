"""Probe: notification timestamp shows 12-hour time and title tooltip with full date+time.

Triggers a boot notification (already fired at app start) by navigating to the app,
then inspects the .af-tm span for:
  1. text matching 12-hour format  (e.g. "3:45 PM", not "15:45:22")
  2. title attribute present with full date+time string

Run:
    just ui-probe                         # (general UI probe — use this probe directly instead)
    uv run python probes/ui_notification_time_probe.py

Requires: frontend running on :3000, CDP Chrome on :9299, backend on :8000.
Screenshots saved to screenshots/.
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome
from _probe_auth import probe_credentials

BASE_URL = "http://localhost:3000"
CDP_PORT = 9299
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

_results: list[tuple[str, bool, str]] = []


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    icon = "✓" if ok else "✗"
    print(f"  {icon}  {label}" + (f"  [{detail}]" if detail else ""))


# 12-hour pattern: optional leading space, hour (1-12), colon, minutes, space, AM/PM
_12H_RE = re.compile(r"^1?[0-9]:[0-5][0-9]\s?(AM|PM)$", re.IGNORECASE)


async def run() -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    username, password = probe_credentials()

    pw, browser = await connect_existing_chrome(CDP_PORT)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

    try:
        # ── Login ────────────────────────────────────────────────────────
        print("\n── Login")
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        await page.evaluate(
            "() => ['af_token','af-auth','af-refresh','af_refresh_token']"
            ".forEach(k => localStorage.removeItem(k))"
        )
        await page.reload(wait_until="networkidle")

        if "/login" in page.url:
            await page.fill('input[type="email"]', username)
            await page.fill('input[type="password"]', password)
            await page.click('button[type="submit"]')
            try:
                await page.wait_for_url(lambda u: "/login" not in u, timeout=10_000)
            except Exception:  # noqa: BLE001
                pass

        _record("Logged in", "/login" not in page.url, page.url)
        if "/login" in page.url:
            return False

        # ── Wait for a notification to appear ────────────────────────────
        print("\n── Notification timestamp")
        # Boot probe fires notifications on load; wait up to 8 s for any .af-tm span
        try:
            await page.wait_for_selector(".af-tm", timeout=8_000)
        except Exception:  # noqa: BLE001
            # No notification visible — trigger one via the notify store exposed on window
            await page.evaluate(
                """() => {
                    const evt = new CustomEvent('af-test-notify', {
                        detail: { title: 'Probe test', severity: 'info', ttl: 8000 }
                    });
                    window.dispatchEvent(evt);
                }"""
            )
            await page.wait_for_timeout(500)

        spans = await page.query_selector_all(".af-tm")
        _record("At least one .af-tm span visible", len(spans) > 0, f"{len(spans)} found")

        if not spans:
            await page.screenshot(path=str(SHOT_DIR / "notif-time-none.png"))
            return False

        # Check every visible notification timestamp
        all_12h = True
        all_have_title = True
        for i, span in enumerate(spans):
            text = (await span.inner_text()).strip()
            title = await span.get_attribute("title")

            is_12h = bool(_12H_RE.match(text))
            has_title = bool(title and len(title) > 5)

            if not is_12h:
                all_12h = False
            if not has_title:
                all_have_title = False

            _record(
                f"span[{i}] text is 12-hour format",
                is_12h,
                repr(text),
            )
            _record(
                f"span[{i}] has title attribute with full datetime",
                has_title,
                repr(title),
            )

        _record("All timestamps are 12-hour", all_12h)
        _record("All timestamps have tooltip title", all_have_title)

        await page.screenshot(path=str(SHOT_DIR / "notif-time-check.png"))
        print(f"\n  Screenshot → screenshots/notif-time-check.png")

    finally:
        await page.close()
        await pw.stop()

    return all(ok for _, ok, _ in _results)


def main() -> None:
    print(f"Notification time probe  →  {BASE_URL}  [CDP :{CDP_PORT}]")
    ok = asyncio.run(run())
    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
