"""Probe: verify model picker popup is not clipped at the viewport top.

Attaches to the existing Chrome CDP session (port 9299), injects a dev JWT,
intercepts /api/v1/iam/me to bypass bootstrap, then exercises the model
picker at three viewport heights to confirm the maxHeight clamp fix works.

Screenshots saved to <repo-root>/screenshots/.

    uv run python probes/ui_model_picker_probe.py
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

import jwt as pyjwt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome

BASE_URL = "http://localhost:3000"
CDP_PORT = 9299
JWT_SECRET = "dev-secret-change-me"
JWT_ALGO = "HS256"
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

_results: list[tuple[str, bool, str]] = []

FAKE_USER = {
    "guid": "00000000-0000-0000-0000-000000000001",
    "email": "probe@local.dev",
    "role": "admin",
    "created_at": "2025-01-01T00:00:00Z",
}


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    icon = "✓" if ok else "✗"
    print(f"  {icon}  {label}" + (f"  {detail}" if detail else ""))


def _mint_token() -> str:
    now = int(time.time())
    payload = {
        "sub": FAKE_USER["guid"],
        "role": FAKE_USER["role"],
        "email": FAKE_USER["email"],
        "iat": now,
        "exp": now + 3600,
    }
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


async def _ensure_rail_open(page) -> None:
    """Re-open the chat rail if it's closed (checks pointer-events, not opacity)."""
    is_open = await page.evaluate("""() => {
        const aside = document.querySelector('[aria-label="Alpha chat"]');
        return aside ? window.getComputedStyle(aside).pointerEvents !== 'none' : false;
    }""")
    if is_open:
        return
    chat_tab = page.get_by_role("tab", name="Chat mode")
    await chat_tab.click()
    await page.wait_for_function("""() => {
        const aside = document.querySelector('[aria-label="Alpha chat"]');
        return aside && window.getComputedStyle(aside).pointerEvents !== 'none';
    }""", timeout=5_000)
    await page.wait_for_timeout(500)


async def _check_popup_fits(page, label: str, shot_name: str) -> bool:
    await _ensure_rail_open(page)

    btn = page.locator('[aria-haspopup="dialog"]').first
    try:
        await btn.wait_for(state="visible", timeout=5_000)
    except Exception as e:
        _record(f"{label}: model picker button visible", False, str(e))
        await page.screenshot(path=str(SHOT_DIR / shot_name))
        return False

    await btn.click()
    await page.wait_for_timeout(350)

    result = await page.evaluate("""() => {
        const menu = document.querySelector('[role="dialog"][aria-label="Model"]');
        if (!menu) return { found: false };
        const r = menu.getBoundingClientRect();
        return {
            found: true,
            top: r.top,
            bottom: r.bottom,
            viewportH: window.innerHeight,
            clippedTop: r.top < 0,
            clippedBottom: r.bottom > window.innerHeight,
        };
    }""")

    await page.screenshot(path=str(SHOT_DIR / shot_name))

    if not result["found"]:
        _record(f"{label}: popup rendered", False, "dialog not in DOM")
        return False

    vh = result["viewportH"]
    top = result["top"]
    bot = result["bottom"]
    _record(f"{label}: popup rendered", True, f"top={top:.0f} bottom={bot:.0f} vh={vh}")
    _record(f"{label}: top not clipped (≥ 0)", not result["clippedTop"], f"top={top:.0f}")
    _record(f"{label}: bottom not clipped (≤ vh)", not result["clippedBottom"],
            f"bottom={bot:.0f} vh={vh}")

    foot = await page.evaluate("""() => {
        const d = document.querySelector('[role="dialog"][aria-label="Model"]');
        if (!d) return { found: false };
        const foot = d.lastElementChild;
        if (!foot) return { found: false };
        const r = foot.getBoundingClientRect();
        return { found: true, top: r.top, bottom: r.bottom, vh: window.innerHeight };
    }""")
    if foot["found"]:
        fv = foot["top"] >= 0 and foot["bottom"] <= foot["vh"]
        _record(f"{label}: footer fully visible", fv,
                f"foot.top={foot['top']:.0f} foot.bottom={foot['bottom']:.0f}")

    # Click the button again to toggle the picker closed (keeps the rail open)
    await btn.click()
    await page.wait_for_timeout(150)
    return not result["clippedTop"] and not result["clippedBottom"]


async def run() -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    token = _mint_token()

    pw, browser = await connect_existing_chrome(CDP_PORT)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

    # Mock /iam/me so bootstrap() succeeds with our fake JWT.
    await page.route("**/api/v1/iam/me", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(FAKE_USER),
    ))

    try:
        print("\n── Inject dev token and navigate to app root")
        await page.goto(BASE_URL, wait_until="domcontentloaded")

        # Write auth state that Zustand persist reads on bootstrap.
        auth_state = json.dumps({
            "state": {
                "accessToken": token,
                "refreshToken": None,
                "user": FAKE_USER,
            },
            "version": 0,
        })
        await page.evaluate(f"""() => {{
            localStorage.setItem('af_token', {json.dumps(token)});
            localStorage.setItem('af-auth', {json.dumps(auth_state)});
            localStorage.removeItem('af_refresh_token');
            localStorage.setItem('af-mode', 'chat');
            sessionStorage.setItem('af-booted', '1');
        }}""")

        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        on_concierge = "/login" not in page.url
        _record("Reached app (not redirected to /login)", on_concierge, page.url)
        if not on_concierge:
            await page.screenshot(path=str(SHOT_DIR / "mp-login-fail.png"))
            return False

        await page.wait_for_timeout(800)

        # Open the chat rail by clicking the CHAT tab
        print("\n── Open chat rail via CHAT tab")
        chat_tab = page.get_by_role("tab", name="Chat mode")
        await chat_tab.wait_for(state="visible", timeout=5_000)
        await chat_tab.click()
        # Wait for chat rail slide-in animation (transition: .42s)
        await page.wait_for_selector('[aria-label="Alpha chat"]', timeout=5_000)
        await page.wait_for_timeout(500)
        _record("Chat rail opened", True)

        print("\n── Normal viewport (900px tall)")
        await page.set_viewport_size({"width": 1280, "height": 900})
        await page.wait_for_timeout(200)
        await _check_popup_fits(page, "Normal 900px", "mp-normal.png")

        print("\n── Short viewport (420px tall) — maxHeight clamp test")
        await page.set_viewport_size({"width": 1280, "height": 420})
        await page.wait_for_timeout(200)
        await _check_popup_fits(page, "Short 420px", "mp-short.png")

        print("\n── Very short viewport (280px) — extreme edge")
        await page.set_viewport_size({"width": 1280, "height": 280})
        await page.wait_for_timeout(200)
        await _check_popup_fits(page, "Very short 280px", "mp-veryshort.png")

    finally:
        await page.set_viewport_size({"width": 1280, "height": 900})
        await page.close()
        await pw.stop()

    return all(ok for _, ok, _ in _results)


def main() -> None:
    print(f"ModelPicker popup clipping probe  →  {BASE_URL}  [CDP :{CDP_PORT}]")
    print(f"Screenshots  →  {SHOT_DIR}/")
    ok = asyncio.run(run())
    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
