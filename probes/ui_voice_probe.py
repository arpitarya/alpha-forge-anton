"""Playwright UI probe — exercises the AlphaForge Anton voice (mic) flow.

Attaches to the existing Chrome CDP session (port 9299), injects a dev JWT,
then mocks window.SpeechRecognition so we can drive the full voice flow without
a real microphone.  Tests:

  1. App reachable (not redirected to /login)
  2. Voice bar renders in the footer
  3. Mic button is present and NOT disabled (supported=true after mount)
  4. Mic button is clickable (user-gesture start doesn't throw)
  5. Listening state becomes active after click
  6. Waveform appears while listening
  7. Transcript fires onFinal and is submitted as a chat query
  8. Listening state resets after recognition ends
  9. Error flow: not-allowed fires notification, button resets to idle

Run:
    uv run python probes/ui_voice_probe.py
    uv run python probes/ui_voice_probe.py --cdp-port 9299 --base http://localhost:3000

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
    await page.goto(base, wait_until="domcontentloaded")
    auth_state = json.dumps({
        "state": {"accessToken": token, "refreshToken": None, "user": FAKE_USER},
        "version": 0,
    })
    await page.evaluate(f"""() => {{
        localStorage.setItem('af_token', {json.dumps(token)});
        localStorage.setItem('af-auth', {json.dumps(auth_state)});
        localStorage.removeItem('af_refresh_token');
        localStorage.setItem('af-mode', 'voice');
        sessionStorage.setItem('af-booted', '1');
    }}""")
    await page.goto(f"{base}/", wait_until="networkidle")
    return "/login" not in page.url


# ---------------------------------------------------------------------------
# SpeechRecognition mock — injected into the page via addInitScript so it
# runs before any React code.  The mock is controllable via window.__srMock.
# ---------------------------------------------------------------------------
SR_MOCK_SCRIPT = """
(function () {
    window.__srMock = {
        instances: [],
        // Call to simulate a successful transcript
        fireResult(transcript) {
            const inst = window.__srMock.instances.at(-1);
            if (!inst) return;
            const fakeEvent = {
                resultIndex: 0,
                results: [{
                    isFinal: true,
                    0: { transcript },
                    length: 1,
                }],
            };
            if (inst.onresult) inst.onresult(fakeEvent);
            if (inst.onend) inst.onend();
        },
        // Call to simulate an error
        fireError(code) {
            const inst = window.__srMock.instances.at(-1);
            if (!inst) return;
            if (inst.onerror) inst.onerror({ error: code });
            if (inst.onend) inst.onend();
        },
        // Check if the latest instance has been started
        get started() {
            const inst = window.__srMock.instances.at(-1);
            return inst ? inst._started : false;
        },
    };

    class MockSR {
        constructor() {
            this.continuous = false;
            this.interimResults = false;
            this.lang = '';
            this.onresult = null;
            this.onerror = null;
            this.onend = null;
            this._started = false;
            window.__srMock.instances.push(this);
        }
        start() { this._started = true; }
        stop()  { this._started = false; if (this.onend) this.onend(); }
        abort() { this._started = false; }
    }

    // Override both variants so getSRCtor() always finds our mock
    window.SpeechRecognition = MockSR;
    window.webkitSpeechRecognition = MockSR;
    // Keep speechSynthesis stub so supported check passes
    if (!window.speechSynthesis) {
        window.speechSynthesis = { speak() {}, cancel() {} };
    }
})();
"""


async def run(base: str, cdp_port: int) -> bool:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    token = _mint_token()

    pw, browser = await connect_existing_chrome(cdp_port)
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()

    # Inject the SR mock before the page JS runs
    await ctx.add_init_script(SR_MOCK_SCRIPT)
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
            await page.screenshot(path=str(SHOT_DIR / "voice-00-login-fail.png"))
            return False
        await page.wait_for_timeout(1_000)  # let React mount + useEffect fire

        # ── 2. Voice bar renders ──────────────────────────────────────────────
        print("\n── Voice bar")
        voice_bar = page.locator("footer.af-voice")
        bar_visible = await voice_bar.is_visible()
        _record("Voice bar footer renders", bar_visible)
        await page.screenshot(path=str(SHOT_DIR / "voice-01-bar.png"))
        if not bar_visible:
            return False

        # ── 3. Mic button enabled ─────────────────────────────────────────────
        print("\n── Mic button state")
        mic_btn = page.get_by_role("button", name="Start listening")
        await mic_btn.wait_for(state="visible", timeout=5_000)
        disabled = await mic_btn.get_attribute("disabled")
        _record("Mic button is enabled (supported=true after mount)", disabled is None,
                f"disabled={disabled!r}")

        # Inspect supported flag via React state (check aria-pressed is accessible)
        aria_pressed = await mic_btn.get_attribute("aria-pressed")
        _record("Mic button has aria-pressed attribute", aria_pressed is not None,
                f"aria-pressed={aria_pressed!r}")

        # ── 4. SR mock is installed ───────────────────────────────────────────
        print("\n── SpeechRecognition mock")
        sr_available = await page.evaluate("() => typeof window.SpeechRecognition === 'function'")
        _record("Mock SpeechRecognition in window", sr_available)

        # ── 5. Clicking mic starts listening ─────────────────────────────────
        print("\n── Start listening")
        await mic_btn.click()
        await page.wait_for_timeout(400)

        sr_started = await page.evaluate("() => window.__srMock.started")
        _record("SpeechRecognition.start() was called", sr_started)

        stop_btn = page.get_by_role("button", name="Stop listening")
        listening_visible = await stop_btn.is_visible()
        _record("Button switches to 'Stop listening' while active", listening_visible)

        await page.screenshot(path=str(SHOT_DIR / "voice-02-listening.png"))

        # ── 6. Waveform appears ───────────────────────────────────────────────
        print("\n── Waveform")
        # VoiceCenter renders <Waveform> only while voice.listening is true
        status_text = await page.locator("footer.af-voice").inner_text()
        _record("Footer shows 'Listening' label while active",
                "Listening" in status_text, repr(status_text[:80]))

        # ── 7. Transcript fires onFinal → chat submission ─────────────────────
        print("\n── Transcript → submit")
        await page.evaluate("() => window.__srMock.fireResult('show my portfolio risk')")
        await page.wait_for_timeout(800)

        # After onFinal, AlphaBar calls onChatModeOpen + onSubmit,
        # which opens the chat rail and creates a user turn
        user_turn = page.locator('text="show my portfolio risk"')
        turn_visible = await user_turn.is_visible()
        _record("Transcript fires onFinal and creates a chat user turn", turn_visible)
        await page.screenshot(path=str(SHOT_DIR / "voice-03-transcript.png"))

        # ── 8. Listening state resets after recognition ends ──────────────────
        print("\n── Listening reset")
        await page.wait_for_timeout(300)
        start_btn_back = page.get_by_role("button", name="Start listening")
        reset_visible = await start_btn_back.is_visible()
        _record("Button resets to 'Start listening' after recognition ends", reset_visible)

        # ── 9. Error flow: not-allowed ─────────────────────────────────────────
        print("\n── Error flow (not-allowed)")
        # Switch back to voice mode and click mic again
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # Reset to voice mode
        await page.evaluate("() => localStorage.setItem('af-mode', 'voice')")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1_000)

        mic_btn2 = page.get_by_role("button", name="Start listening")
        await mic_btn2.wait_for(state="visible", timeout=5_000)
        await mic_btn2.click()
        await page.wait_for_timeout(300)
        await page.evaluate("() => window.__srMock.fireError('not-allowed')")
        await page.wait_for_timeout(600)

        # A notification toast should appear
        notif = page.locator("text=Voice input failed")
        notif_visible = await notif.is_visible()
        _record("not-allowed error shows 'Voice input failed' notification", notif_visible)

        # Button should be back to idle (not stuck in listening)
        idle_btn = page.get_by_role("button", name="Start listening")
        idle_after_err = await idle_btn.is_visible()
        _record("Mic button returns to idle after error", idle_after_err)

        await page.screenshot(path=str(SHOT_DIR / "voice-04-error.png"))

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

    print(f"Voice UI Probe  →  {args.base}  [CDP :{args.cdp_port}]")
    print(f"Screenshots  →  {SHOT_DIR}/")

    ok = asyncio.run(run(args.base, args.cdp_port))

    print("\n── Summary")
    passed = sum(1 for _, o, _ in _results if o)
    failed = [label for label, o, _ in _results if not o]
    print(f"  {passed}/{len(_results)} checks passed")
    if failed:
        print("  Failed:")
        for f in failed:
            print(f"    ✗ {f}")
    print(f"  Screenshots → {SHOT_DIR}/")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
