"""Playwright UI probe — exercises the AlphaForge Anton voice (mic) flow.

Attaches to the existing Chrome CDP session (port 9299), injects a dev JWT,
then mocks:
  * navigator.mediaDevices.getUserMedia  → returns a fake MediaStream
  * window.MediaRecorder                  → records a few chunks, fires onstop
  * fetch('/api/v1/concierge/stt')        → returns a canned transcript

Tests:
  1. App reachable (not redirected to /login)
  2. Voice bar renders in the footer
  3. Mic button enabled (supported=true after mount)
  4. Click → getUserMedia called, MediaRecorder.start() called, listening=true
  5. Click again → MediaRecorder.stop() called, /stt POST fires, transcript received
  6. Transcript opens chat rail and creates a user turn
  7. Error flow: getUserMedia NotAllowedError → notification shows, button idle

Run:
    uv run python probes/ui_voice_probe.py
    uv run python probes/ui_voice_probe.py --cdp-port 9299 --base https://localhost:3000
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

CANNED_TRANSCRIPT = "show my portfolio risk"


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


def _build_mock(simulate_denied: bool) -> str:
    return f"""
(function () {{
    window.__voiceMock = {{
        simulateDenied: {str(simulate_denied).lower()},
        recorderStarted: 0,
        recorderStopped: 0,
        gumCalled: 0,
        sttPosted: 0,
    }};

    class FakeTrack {{
        constructor() {{ this.kind = 'audio'; this.label = 'fake-mic'; this.readyState = 'live'; }}
        stop() {{ this.readyState = 'ended'; }}
    }}
    class FakeStream {{
        constructor() {{ this._tracks = [new FakeTrack()]; }}
        getTracks() {{ return this._tracks; }}
        getAudioTracks() {{ return this._tracks; }}
    }}

    if (!navigator.mediaDevices) navigator.mediaDevices = {{}};
    navigator.mediaDevices.getUserMedia = async function () {{
        window.__voiceMock.gumCalled++;
        if (window.__voiceMock.simulateDenied) {{
            const err = new Error('Permission denied');
            err.name = 'NotAllowedError';
            throw err;
        }}
        return new FakeStream();
    }};

    class MockRecorder extends EventTarget {{
        constructor(stream, opts) {{
            super();
            this.stream = stream;
            this.mimeType = (opts && opts.mimeType) || 'audio/webm';
            this.state = 'inactive';
            this.ondataavailable = null;
            this.onstop = null;
            this.onerror = null;
        }}
        start() {{
            this.state = 'recording';
            window.__voiceMock.recorderStarted++;
            setTimeout(() => {{
                if (this.ondataavailable) {{
                    const blob = new Blob(['fake-audio-bytes'], {{ type: this.mimeType }});
                    this.ondataavailable({{ data: blob }});
                }}
            }}, 50);
        }}
        stop() {{
            if (this.state !== 'recording') return;
            this.state = 'inactive';
            window.__voiceMock.recorderStopped++;
            setTimeout(() => {{ if (this.onstop) this.onstop(); }}, 20);
        }}
    }}
    MockRecorder.isTypeSupported = () => true;
    window.MediaRecorder = MockRecorder;

    const origFetch = window.fetch.bind(window);
    window.fetch = async function (input, init) {{
        const url = typeof input === 'string' ? input : input.url;
        if (url && url.includes('/api/v1/concierge/stt')) {{
            window.__voiceMock.sttPosted++;
            return new Response(
                JSON.stringify({{ transcript: {json.dumps(CANNED_TRANSCRIPT)} }}),
                {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }},
            );
        }}
        return origFetch(input, init);
    }};
}})();
"""


async def _inject_auth_and_navigate(page, base: str, token: str, mock_script: str) -> bool:
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
    await page.add_init_script(mock_script)
    await page.goto(f"{base}/", wait_until="networkidle")
    return "/login" not in page.url


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
        print("\n── Auth bypass + navigation")
        on_app = await _inject_auth_and_navigate(
            page, base, token, _build_mock(simulate_denied=False)
        )
        _record("Reached app (not /login)", on_app, page.url)
        if not on_app:
            await page.screenshot(path=str(SHOT_DIR / "voice-00-login-fail.png"))
            return False
        await page.wait_for_timeout(800)

        print("\n── Voice bar")
        voice_bar = page.locator("footer.af-voice")
        bar_visible = await voice_bar.is_visible()
        _record("Voice bar footer renders", bar_visible)
        await page.screenshot(path=str(SHOT_DIR / "voice-01-bar.png"))
        if not bar_visible:
            return False

        print("\n── Mic button state")
        mic_btn = page.get_by_role("button", name="Start listening")
        await mic_btn.wait_for(state="visible", timeout=5_000)
        disabled = await mic_btn.get_attribute("disabled")
        _record("Mic button is enabled (supported=true after mount)", disabled is None,
                f"disabled={disabled!r}")

        print("\n── Start recording")
        await mic_btn.click()
        await page.wait_for_timeout(300)

        gum_called = await page.evaluate("() => window.__voiceMock.gumCalled")
        _record("getUserMedia called", gum_called >= 1, f"calls={gum_called}")
        rec_started = await page.evaluate("() => window.__voiceMock.recorderStarted")
        _record("MediaRecorder.start() called", rec_started >= 1, f"starts={rec_started}")

        stop_btn = page.get_by_role("button", name="Stop listening")
        listening_visible = await stop_btn.is_visible()
        _record("Button switches to 'Stop listening'", listening_visible)
        await page.screenshot(path=str(SHOT_DIR / "voice-02-listening.png"))

        print("\n── Stop + transcribe")
        await stop_btn.click()
        await page.wait_for_timeout(800)

        rec_stopped = await page.evaluate("() => window.__voiceMock.recorderStopped")
        _record("MediaRecorder.stop() called", rec_stopped >= 1, f"stops={rec_stopped}")

        stt_posted = await page.evaluate("() => window.__voiceMock.sttPosted")
        _record("POST /api/v1/concierge/stt fired", stt_posted >= 1, f"posts={stt_posted}")

        print("\n── Transcript → chat rail")
        await page.wait_for_timeout(500)
        user_turn = page.locator(f'text="{CANNED_TRANSCRIPT}"')
        turn_visible = await user_turn.is_visible()
        _record("Transcript creates a chat user turn", turn_visible)
        await page.screenshot(path=str(SHOT_DIR / "voice-03-transcript.png"))

        rail_open = await page.evaluate("""() => {
            const aside = document.querySelector('[aria-label="Alpha chat"]');
            if (!aside) return false;
            return window.getComputedStyle(aside).pointerEvents !== 'none';
        }""")
        _record("Chat rail opens after transcript", rail_open)

        print("\n── Error flow (NotAllowedError)")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(300)
        await page.evaluate("() => localStorage.setItem('af-mode', 'voice')")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(800)
        # Flip the live mock flag (init script re-installed a fresh one on reload)
        await page.evaluate("() => { window.__voiceMock.simulateDenied = true; }")

        mic_btn2 = page.get_by_role("button", name="Start listening")
        await mic_btn2.wait_for(state="visible", timeout=5_000)
        await mic_btn2.click()
        await page.wait_for_timeout(600)

        notif = page.locator("text=Voice input failed")
        notif_visible = await notif.is_visible()
        _record("NotAllowedError shows 'Voice input failed' notification", notif_visible)

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
