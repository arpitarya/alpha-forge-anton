"""Claude SDK Phase-1 probe — block-walk safety + fixture stream reassembly.

Run:  just probe claude-stream
Standalone — no ANTHROPIC_API_KEY or CDP required.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "concierge" / "llm" / "src"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _b(type_: str, **kw) -> SimpleNamespace:
    return SimpleNamespace(type=type_, **kw)


def main() -> int:
    from alphaforge_anton_llm.providers._claude_stream import claude_stream
    from alphaforge_anton_llm.providers.claude_sdk import ClaudeSdkAdapter, _parse_blocks

    # ── block walk ──
    check("text blocks concatenate",
          _parse_blocks([_b("text", text="Hello "), _b("text", text="world")]) == "Hello world")
    check("tool_use first block doesn't crash",
          _parse_blocks([_b("tool_use", id="t1", name="fn", input={}), _b("text", text="ok")]) == "ok")
    check("thinking block skipped in text output",
          _parse_blocks([_b("thinking", thinking="hmm"), _b("text", text="yes")]) == "yes")
    check("empty blocks → empty string", _parse_blocks([]) == "")

    # ── adapter flags ──
    adapter = ClaudeSdkAdapter()
    check("supports_streaming is True", adapter.supports_streaming is True)
    check("astream method exists", hasattr(adapter, "astream"))

    # ── fixture stream reassembly ──
    events = [
        SimpleNamespace(type="message_start",
                        message=SimpleNamespace(usage=SimpleNamespace(input_tokens=10))),
        SimpleNamespace(type="content_block_delta",
                        delta=SimpleNamespace(type="text_delta", text="Hello")),
        SimpleNamespace(type="content_block_delta",
                        delta=SimpleNamespace(type="text_delta", text=", world")),
        SimpleNamespace(type="message_delta",
                        usage=SimpleNamespace(output_tokens=5)),
    ]

    class FakeStream:
        def __init__(self) -> None:
            self._it = iter(events)

        def __aiter__(self): return self

        async def __anext__(self):
            try:
                return next(self._it)
            except StopIteration:
                raise StopAsyncIteration

        async def __aenter__(self): return self
        async def __aexit__(self, *_): pass

    class FakeClient:
        class messages:
            @staticmethod
            def stream(**kw): return FakeStream()

    async def _run() -> list:
        return [snap async for snap in claude_stream(
            client=FakeClient(), model="claude-sonnet-4-6", provider_name="claude-sdk", kw={},
        )]

    snaps = asyncio.run(_run())
    final = snaps[-1]
    check("fixture stream reassembles to full text", final.content == "Hello, world")
    check("intermediate snapshot grows cumulatively",
          any(s.content == "Hello" for s in snaps))
    check("final snapshot has input_tokens=10", final.prompt_tokens == 10)
    check("final snapshot has output_tokens=5", final.completion_tokens == 5)

    print("\n" + ("❌ claude-sdk Phase-1 drift" if _fail else "✅ claude-sdk Phase-1 streaming intact"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
