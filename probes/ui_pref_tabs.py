"""Capture every Preferences tab so the design implementation can be reviewed."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome
from _probe_auth import probe_credentials

BASE_URL = os.getenv("AF_FRONTEND", "http://localhost:3000")
CDP_PORT = int(os.getenv("BROKER_CDP_PORT", "9299"))
USERNAME, PASSWORD = probe_credentials()
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

TABS = ["Appearance", "Display", "Markets", "Alpha AI", "Notifications", "Account", "Privacy", "About"]


async def main() -> None:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, browser = await connect_existing_chrome(CDP_PORT)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

    # Log in via the UI to get a valid session
    await page.goto(BASE_URL, wait_until="domcontentloaded")
    await page.evaluate("() => localStorage.removeItem('af_token')")
    await page.goto(BASE_URL, wait_until="networkidle")

    if "/login" not in page.url:
        print("  ! Already logged in, reusing session")
    else:
        await page.fill('input[type="text"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        try:
            await page.wait_for_url(lambda url: "/login" not in url, timeout=10_000)
        except Exception:  # noqa: BLE001
            print("  ✗ Login failed — is the backend running?")
            await pw.stop()
            return

    try:
        await page.set_viewport_size({"width": 1440, "height": 900})
        await page.goto(f"{BASE_URL}/preferences", wait_until="networkidle", timeout=45_000)
        await page.wait_for_selector("aside", timeout=20_000)
        await page.wait_for_timeout(800)

        # Full-page screenshot before clicking tabs
        out = SHOT_DIR / "preferences-full.png"
        await page.screenshot(path=str(out), full_page=True)
        print(f"  ✓ Full page   → {out.name}")

        for tab in TABS:
            slug = tab.lower().replace(" ", "-")
            btn = page.locator("aside button", has_text=tab).first
            try:
                await btn.wait_for(timeout=5_000)
                await btn.click()
                await page.wait_for_timeout(550)
            except Exception:  # noqa: BLE001
                print(f"  ✗ {tab:<13}  (tab not found in sidebar)")
                continue
            out = SHOT_DIR / f"preferences-{slug}.png"
            await page.screenshot(path=str(out))
            print(f"  ✓ {tab:<13} → {out.name}")
    finally:
        await page.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
