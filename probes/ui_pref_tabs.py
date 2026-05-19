"""Capture every Preferences tab so the design implementation can be reviewed."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome

BASE_URL = os.getenv("AF_FRONTEND", "http://localhost:3000")
CDP_PORT = int(os.getenv("BROKER_CDP_PORT", "9299"))
USERNAME = os.getenv("PROBE_USER", "admin")
PASSWORD = os.getenv("PROBE_PASS", "alphaforge-anton-dev")
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

TABS = ["Appearance", "Display", "Markets", "Alpha AI", "Notifications", "Account", "Privacy", "About"]


async def main() -> None:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, browser = await connect_existing_chrome(CDP_PORT)
    ctx = browser.contexts[0]
    page = await ctx.new_page()

    import httpx  # noqa: PLC0415

    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(
            "http://localhost:8000/api/v1/auth/token",
            data={"username": USERNAME, "password": PASSWORD},
        )
        token = r.json()["access_token"]

    try:
        await page.set_viewport_size({"width": 1440, "height": 900})
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        await page.evaluate(f"() => localStorage.setItem('af_token', {token!r})")
        await page.goto(f"{BASE_URL}/preferences", wait_until="networkidle", timeout=45_000)
        await page.wait_for_selector("aside", timeout=20_000)
        await page.wait_for_timeout(800)
        for tab in TABS:
            slug = tab.lower().replace(" ", "-")
            # click the sidebar button that contains the label text
            btn = page.locator("aside button", has_text=tab).first
            await btn.click()
            await page.wait_for_timeout(550)
            out = SHOT_DIR / f"preferences-{slug}.png"
            await page.screenshot(path=str(out))
            print(f"  ✓ {tab:<13} → {out.name}")
    finally:
        await page.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
