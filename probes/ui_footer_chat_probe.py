"""Playwright UI probe — exercises the Command Console footer bar and chat popup.

Attaches to the existing Chrome CDP session (port 9299), injects a dev JWT,
and exercises:

  1. App reachable (not redirected to /login)
  2. Footer renders: .af-voice exists, mode segment shows Voice + Chat tabs
  3. Mode-seg height parity: container is 26px; buttons rendered at 24px (border-box)
  4. Chat mode activates: clicking Chat tab shows #chatinput-bar (footer textarea)
  5. Fu-chips in EmptyState: before any submission the aside DOM has stacked fu-chips
  6. ComposeCard grows: typing a long message makes the footer grow (multiline)
  7. Submit opens rail: pressing Enter opens the chat rail popup
  8. Chat rail has left nav sidebar: <nav aria-label="Alpha modes"> is 58px wide
  9. Chat rail header: "Conversation" title + "online" chip visible
 10. ESC closes rail
 11. Double-click toggle: double-clicking the Voice/Chat toggle reopens the rail

Run:
    uv run python probes/ui_footer_chat_probe.py
    uv run python probes/ui_footer_chat_probe.py --cdp-port 9299 --base https://localhost:3000

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

DEFAULT_BASE = "https://localhost:3000"
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
    await page.goto(base, wait_until="domcontentloaded")
    auth_state = json.dumps({
        "state": {"accessToken": token, "refreshToken": None, "user": FAKE_USER},
        "version": 0,
    })
    await page.evaluate(f"""() => {{
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        localStorage.setItem('af-boot-done', '1');
        localStorage.setItem('af-mode', 'voice');
    }}""")
    await page.goto(base, wait_until="domcontentloaded")
    await page.wait_for_timeout(1200)
    return "/login" not in page.url


async def _rail_is_open(page) -> bool:
    return await page.evaluate("""() => {
        const aside = document.querySelector('[aria-label="Alpha chat"]');
        if (!aside) return false;
        return window.getComputedStyle(aside).pointerEvents !== 'none';
    }""")


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    token = _mint_token()

    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()

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
            await page.screenshot(path=str(SHOT_DIR / "ci-footer-login-fail.png"))
            return False
        await page.wait_for_timeout(800)

        # ── 2. Footer renders ─────────────────────────────────────────────────
        print("\n── Footer bar")
        footer = page.locator("footer.af-voice")
        _record("Footer .af-voice present", await footer.count() > 0)
        voice_tab = page.get_by_role("tab", name="Voice mode")
        chat_tab = page.get_by_role("tab", name="Chat mode")
        _record("Voice tab present", await voice_tab.count() > 0)
        _record("Chat tab present", await chat_tab.count() > 0)
        await page.screenshot(path=str(SHOT_DIR / "ci-footer-01-voice.png"))

        # ── 3. Mode-seg height parity ─────────────────────────────────────────
        # Container is 26px (border-box). With 1px border top+bottom the buttons
        # rendered height is 24px — both tabs must be equal and ≥ 24px.
        print("\n── Mode-seg height parity")
        heights = await page.evaluate("""() => {
            const tabs = [...document.querySelectorAll(
                '[role="tablist"][aria-label="Input mode"] [role="tab"]'
            )];
            return tabs.map(t => parseFloat(window.getComputedStyle(t).height));
        }""")
        if heights and len(heights) >= 2:
            _record("Voice tab height ≥ 24px", heights[0] >= 24, f"{heights[0]:.1f}px")
            _record("Chat tab height ≥ 24px", heights[1] >= 24, f"{heights[1]:.1f}px")
            _record("Tab heights are equal", abs(heights[0] - heights[1]) < 1,
                    f"{heights[0]:.1f} vs {heights[1]:.1f}")
        else:
            _record("Mode-seg tabs found", False, f"found {len(heights)} tabs")

        # ── 3b. Voice-bar model picker is clickable ───────────────────────────
        # The model label in the voice bar is now the ModelPicker dropdown button.
        print("\n── Voice-bar model picker (clickable)")
        picker_btn = page.locator(
            'footer.af-voice [data-component="ModelPicker"] button[aria-haspopup="dialog"]'
        )
        _record("Model picker button present in voice bar", await picker_btn.count() > 0)
        if await picker_btn.count() > 0:
            # JS dispatch avoids coordinate hit-testing against the footer overlay
            await page.evaluate(
                "() => document.querySelector("
                "'footer.af-voice [data-component=\"ModelPicker\"] "
                "button[aria-haspopup=\"dialog\"]')?.click()"
            )
            await page.wait_for_timeout(300)
            dialog_open = await page.evaluate(
                "() => !!document.querySelector('[role=\"dialog\"][aria-label=\"Model\"]')"
            )
            _record("Clicking model label opens picker dialog", dialog_open)
            await page.screenshot(path=str(SHOT_DIR / "ci-footer-01b-picker.png"))
            # close it again before continuing
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(200)

        # ── 4. Chat mode shows footer textarea ────────────────────────────────
        print("\n── Chat mode (footer textarea)")
        await chat_tab.click()
        await page.wait_for_timeout(400)
        footer_ta = page.locator("#chatinput-bar")
        _record("Footer textarea visible after Chat click", await footer_ta.is_visible())
        await page.screenshot(path=str(SHOT_DIR / "ci-footer-02-chat.png"))

        # ── 5. Fu-chips in EmptyState (checked before any submission) ─────────
        # The rail <aside> is always in the DOM; EmptyState shows when turns=0.
        # Fu-chips are grid buttons: gridTemplateColumns has 3 values (34px 1fr auto).
        print("\n── EmptyState fu-chips (pre-submission)")
        chip_layout = await page.evaluate("""() => {
            const aside = document.querySelector('[aria-label="Alpha chat"]');
            if (!aside) return null;
            const chips = [...aside.querySelectorAll('button[type="button"]')].filter(b => {
                const cols = window.getComputedStyle(b).gridTemplateColumns;
                if (!cols || !cols.includes('px')) return false;
                const parts = cols.trim().split(/\\s+/);
                return parts.length === 3;
            });
            if (chips.length < 2) return { count: chips.length, allSameLeft: false };
            const rects = chips.map(c => c.getBoundingClientRect());
            const lefts = rects.map(r => Math.round(r.left));
            const allSameLeft = lefts.every(l => Math.abs(l - lefts[0]) < 4);
            return { count: chips.length, allSameLeft };
        }""")
        if chip_layout:
            _record(f"Fu-chips found ({chip_layout['count']})", chip_layout['count'] >= 2)
            _record("Fu-chips stacked in single column", chip_layout['allSameLeft'],
                    "all share same left edge")
        else:
            _record("Fu-chips found", False, "aside not in DOM")

        # ── 6. ComposeCard grows on multiline content ─────────────────────────
        print("\n── ComposeCard multiline")
        long_text = "This is a long message that should trigger the compose card expansion. " * 3
        await footer_ta.fill(long_text)
        await page.wait_for_timeout(300)
        footer_h_after = await page.evaluate("""() => {
            const f = document.querySelector('footer.af-voice');
            return f ? parseFloat(window.getComputedStyle(f).height) : 0;
        }""")
        _record("Footer height > 36px (compose card expanded)", footer_h_after > 36,
                f"{footer_h_after:.0f}px")
        await page.screenshot(path=str(SHOT_DIR / "ci-footer-03-compose.png"))

        # ── 7. Submit opens chat rail ─────────────────────────────────────────
        print("\n── Chat rail opens on submit")
        await footer_ta.fill("What is my portfolio worth today?")
        await footer_ta.press("Enter")
        try:
            await page.wait_for_function("""() => {
                const aside = document.querySelector('[aria-label="Alpha chat"]');
                return aside && window.getComputedStyle(aside).pointerEvents !== 'none';
            }""", timeout=6_000)
            _record("Chat rail opened after footer submit", True)
        except Exception as e:
            _record("Chat rail opened after footer submit", False, str(e))
        await page.wait_for_timeout(600)
        await page.screenshot(path=str(SHOT_DIR / "ci-footer-04-rail-open.png"))

        # ── 8. Left nav sidebar ───────────────────────────────────────────────
        print("\n── Left nav sidebar")
        nav_w = await page.evaluate("""() => {
            const nav = document.querySelector('[aria-label="Alpha modes"]');
            return nav ? parseFloat(window.getComputedStyle(nav).width) : -1;
        }""")
        _record("Left nav sidebar present", nav_w > 0, f"{nav_w:.0f}px wide")
        _record("Left nav sidebar is 58px", abs(nav_w - 58) < 4, f"{nav_w:.1f}px")

        # ── 9. Chat rail header ───────────────────────────────────────────────
        print("\n── Chat rail header")
        conversation_title = await page.evaluate("""() => {
            const aside = document.querySelector('[aria-label="Alpha chat"]');
            if (!aside) return '';
            const all = aside.querySelectorAll('*');
            for (const el of all) {
                if (el.textContent?.trim() === 'Conversation' && el.children.length === 0)
                    return el.textContent.trim();
            }
            return '';
        }""")
        _record("'Conversation' title present in header", conversation_title == "Conversation",
                repr(conversation_title))

        # "online" chip: outer span has a dot child + "online" text node (children.length=1)
        online_chip = await page.evaluate("""() => {
            const aside = document.querySelector('[aria-label="Alpha chat"]');
            if (!aside) return false;
            const all = [...aside.querySelectorAll('*')];
            return all.some(el => el.textContent?.trim().toLowerCase() === 'online');
        }""")
        _record("Online chip visible in header", online_chip)

        # ── 10. ESC closes rail ───────────────────────────────────────────────
        print("\n── ESC closes rail")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)
        rail_closed = not await _rail_is_open(page)
        _record("ESC closes chat rail", rail_closed)
        await page.screenshot(path=str(SHOT_DIR / "ci-footer-05-closed.png"))

        # ── 11. Double-click toggle reopens rail ──────────────────────────────
        # Shortcut: double-clicking the Voice/Chat toggle opens the chat rail
        # directly, without first submitting a message.
        print("\n── Double-click toggle reopens rail")
        await chat_tab.dblclick()
        try:
            await page.wait_for_function("""() => {
                const aside = document.querySelector('[aria-label="Alpha chat"]');
                return aside && window.getComputedStyle(aside).pointerEvents !== 'none';
            }""", timeout=4_000)
            _record("Double-click toggle opens chat rail", True)
        except Exception as e:
            _record("Double-click toggle opens chat rail", False, str(e))
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(SHOT_DIR / "ci-footer-06-dblclick-open.png"))

    finally:
        await page.close()
        await pw.stop()

    # ── Summary ───────────────────────────────────────────────────────────────
    passed = sum(1 for _, ok, _ in _results if ok)
    total = len(_results)
    print(f"\n── {passed}/{total} checks passed")
    return passed == total


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Footer bar + chat popup probe")
    p.add_argument("--cdp-port", type=int, default=DEFAULT_CDP)
    p.add_argument("--base", default=DEFAULT_BASE)
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    ok = asyncio.run(run(args.base, args.cdp_port))
    sys.exit(0 if ok else 1)
