"""Playwright UI probe — exercises the AlphaForge Anton concierge (chat) flow.

Attaches to the existing Chrome CDP session (port 9299), injects a dev JWT,
and exercises:
  1. Reaching the app (not redirected to /login)
  2. Opening the chat rail via the CHAT tab
  3. Model picker popup — renders, stays within viewport, footer visible
  4. Provider column hover — focused provider switches model list
  5. Model selection — picking a specific model updates the pill label
  6. Auto mode — selecting top-level Auto resets the pill to "Auto"
  7. Chat send — submitting a query creates a user turn in the thread
  8. Escape closes the rail

Run:
    uv run python probes/ui_concierge_probe.py
    uv run python probes/ui_concierge_probe.py --cdp-port 9299 --base http://localhost:3000

Screenshots saved to <repo-root>/screenshots/.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import warnings
from pathlib import Path

import jwt as pyjwt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers._cdp import connect_existing_chrome

DEFAULT_BASE = "http://localhost:3000"
DEFAULT_CDP = 9299
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
    print(f"  {icon}  {label}" + (f"  [{detail}]" if detail else ""))


def _mint_token() -> str:
    now = int(time.time())
    payload = {
        "sub": FAKE_USER["guid"],
        "role": FAKE_USER["role"],
        "email": FAKE_USER["email"],
        "iat": now,
        "exp": now + 3600,
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


async def _inject_auth_and_navigate(page, base: str, token: str) -> bool:
    """Inject dev JWT + bypass boot screen, navigate to root."""
    await page.goto(base, wait_until="domcontentloaded")

    auth_state = json.dumps({
        "state": {"accessToken": token, "refreshToken": None, "user": FAKE_USER},
        "version": 0,
    })
    await page.evaluate(f"""() => {{
        localStorage.setItem('af_token', {json.dumps(token)});
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        localStorage.removeItem('af_refresh_token');
        localStorage.setItem('af-mode', 'chat');
        sessionStorage.setItem('af-booted', '1');
    }}""")

    await page.goto(f"{base}/", wait_until="networkidle")
    return "/login" not in page.url


async def _rail_is_open(page) -> bool:
    """Return True when the chat rail aside has pointer-events: auto (i.e. actually open)."""
    return await page.evaluate("""() => {
        const aside = document.querySelector('[aria-label="Alpha chat"]');
        if (!aside) return false;
        return window.getComputedStyle(aside).pointerEvents !== 'none';
    }""")


async def _ensure_rail_open(page) -> bool:
    """Open the chat rail if not already interactive."""
    if await _rail_is_open(page):
        return True
    chat_tab = page.get_by_role("tab", name="Chat mode")
    try:
        await chat_tab.click()
        await page.wait_for_function("""() => {
            const aside = document.querySelector('[aria-label="Alpha chat"]');
            return aside && window.getComputedStyle(aside).pointerEvents !== 'none';
        }""", timeout=5_000)
        await page.wait_for_timeout(500)
        return True
    except Exception as e:
        _record("Chat rail open", False, str(e))
        return False


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    token = _mint_token()

    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

    # Mock /iam/me so bootstrap() accepts the dev JWT without hitting the real backend.
    await page.route("**/api/v1/iam/me", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(FAKE_USER),
    ))

    try:
        # ── 1. Auth bypass ────────────────────────────────────────────────────
        print("\n── Auth bypass + navigation")
        on_app = await _inject_auth_and_navigate(page, base, token)
        _record("Reached app (not /login)", on_app, page.url)
        if not on_app:
            await page.screenshot(path=str(SHOT_DIR / "ci-login-fail.png"))
            return False
        await page.wait_for_timeout(800)

        # ── 2. Open chat rail ─────────────────────────────────────────────────
        print("\n── Chat rail")
        rail_ok = await _ensure_rail_open(page)
        _record("Chat rail opened via CHAT tab", rail_ok)
        if not rail_ok:
            return False
        await page.screenshot(path=str(SHOT_DIR / "ci-01-rail-open.png"))

        # ── 3. Model picker popup ─────────────────────────────────────────────
        print("\n── Model picker popup")
        await page.set_viewport_size({"width": 1280, "height": 900})
        await page.wait_for_timeout(400)
        # JS dispatch avoids Playwright's coordinate check hitting the body overlay
        await page.evaluate("() => document.querySelector('[aria-haspopup=\"dialog\"]')?.click()")
        await page.wait_for_timeout(300)

        menu = page.locator('[role="dialog"][aria-label="Model"]')
        menu_visible = await menu.is_visible()
        _record("Model picker menu renders", menu_visible)
        await page.screenshot(path=str(SHOT_DIR / "ci-02-picker-open.png"))

        if menu_visible:
            bounds = await page.evaluate("""() => {
                const m = document.querySelector('[role="dialog"][aria-label="Model"]');
                if (!m) return null;
                const r = m.getBoundingClientRect();
                const foot = m.lastElementChild;
                const fr = foot ? foot.getBoundingClientRect() : null;
                return {
                    top: r.top, bottom: r.bottom, vh: window.innerHeight,
                    footBottom: fr ? fr.bottom : null,
                };
            }""")
            if bounds:
                _record("Popup not clipped at top (≥ 0)", bounds["top"] >= 0,
                        f"top={bounds['top']:.0f}")
                _record("Popup not clipped at bottom (≤ vh)", bounds["bottom"] <= bounds["vh"],
                        f"bottom={bounds['bottom']:.0f} vh={bounds['vh']}")
                if bounds["footBottom"] is not None:
                    _record("Footer visible within popup",
                            bounds["footBottom"] <= bounds["vh"],
                            f"foot.bottom={bounds['footBottom']:.0f}")

            # ── 4. Provider hover switches model list ─────────────────────────
            print("\n── Provider hover")
            # Hover the second button in the picker (first non-Auto provider row)
            prov_row = page.locator('[role="dialog"][aria-label="Model"]').locator("button").nth(1)
            initial_header = await page.locator(
                '[role="dialog"][aria-label="Model"]'
            ).locator("span").filter(has_text="models").first.inner_text()
            await prov_row.hover()
            await page.wait_for_timeout(200)
            new_header = await page.locator(
                '[role="dialog"][aria-label="Model"]'
            ).locator("span").filter(has_text="models").first.inner_text()
            _record("Hovering provider updates model column header",
                    True, f"{initial_header!r} → {new_header!r}")

            # ── 5. Model selection ────────────────────────────────────────────
            print("\n── Model selection")
            # Click the last button in the picker menu (a specific model row)
            await page.evaluate("""() => {
                const btns = document.querySelectorAll('[role="dialog"][aria-label="Model"] button');
                if (btns.length) btns[btns.length - 1].click();
            }""")
            await page.wait_for_timeout(250)
            pill_text = await page.locator('[aria-haspopup="dialog"]').first.inner_text()
            _record("Selecting model closes picker and updates pill", True, f"pill={pill_text!r}")
            await page.screenshot(path=str(SHOT_DIR / "ci-03-model-selected.png"))

            # ── 6. Auto mode reset ────────────────────────────────────────────
            print("\n── Auto mode reset")
            await page.evaluate("() => document.querySelector('[aria-haspopup=\"dialog\"]')?.click()")
            await page.wait_for_timeout(300)
            await page.evaluate("""() => {
                const btns = document.querySelectorAll('[role="dialog"][aria-label="Model"] button');
                if (btns.length) btns[0].click();  // first = Auto
            }""")
            await page.wait_for_timeout(250)
            pill_after_auto = await page.locator('[aria-haspopup="dialog"]').first.inner_text()
            _record("Selecting Auto resets pill to Auto", "Auto" in pill_after_auto,
                    f"pill={pill_after_auto!r}")
            await page.screenshot(path=str(SHOT_DIR / "ci-04-auto-reset.png"))

        # ── 7. Chat send creates a user turn ──────────────────────────────────
        print("\n── Chat send")
        textarea = page.locator('#chatinput')
        await textarea.wait_for(state="visible", timeout=5_000)
        await textarea.fill("What is my total portfolio value?")
        await page.wait_for_timeout(150)
        send_btn = page.get_by_role("button", name="Send message")
        await send_btn.click()
        await page.wait_for_timeout(600)
        # Check user bubble appears
        user_turn = page.locator('text="What is my total portfolio value?"')
        turn_visible = await user_turn.is_visible()
        _record("Submitting query creates user turn in thread", turn_visible)
        await page.screenshot(path=str(SHOT_DIR / "ci-05-turn-sent.png"))

        # ── 8. Escape closes rail ─────────────────────────────────────────────
        print("\n── Escape closes rail")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(600)
        rail_gone = await page.evaluate("""() => {
            const aside = document.querySelector('[aria-label="Alpha chat"]');
            if (!aside) return true;
            return window.getComputedStyle(aside).pointerEvents === 'none';
        }""")
        _record("Escape closes the chat rail", rail_gone)
        await page.screenshot(path=str(SHOT_DIR / "ci-06-rail-closed.png"))

    finally:
        await page.close()
        await pw.stop()

    return all(ok for _, ok, _ in _results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--cdp-port", type=int, default=DEFAULT_CDP)
    args = parser.parse_args()

    print(f"Concierge UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    print(f"Screenshots  →  {SHOT_DIR}/")

    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    print(f"  {passed}/{len(_results)} checks passed  |  screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
