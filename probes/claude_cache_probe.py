"""Phase 3 prompt-caching probe — standalone, no API, no CDP.

Asserts: cacheable-prefix marking in prompt_service, cache_control placement in the
adapter's system block array, cache-aware pricing (manifest rates), and cache-token
capture in the stream. Run: just probe claude-cache
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "concierge" / "llm" / "src"))
sys.path.insert(0, str(ROOT / "backend"))
_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _adapter_and_pricing() -> None:
    from alphaforge_anton_llm import pricing
    from alphaforge_anton_llm.providers._claude_system import system_blocks
    from alphaforge_anton_llm.types import Message
    msgs = [Message(role="system", content=c, cacheable=cc) for c, cc in
            [("SYS", True), ("OBJ", True), ("MEM", True), ("FUX", False), ("HOLD", False)]]
    msgs.append(Message(role="user", content="hi"))
    blocks = system_blocks(msgs)
    check("system → 5 text blocks (user excluded)", len(blocks) == 5)
    check("cacheable blocks come first", [b["text"] for b in blocks[:3]] == ["SYS", "OBJ", "MEM"])
    check("cache_control on exactly the last cacheable block",
          [i for i, b in enumerate(blocks) if "cache_control" in b] == [2])
    check("breakpoint is ephemeral", blocks[2].get("cache_control") == {"type": "ephemeral"})
    check("volatile blocks carry no cache_control", all("cache_control" not in b for b in blocks[3:]))
    check("all-volatile → no breakpoint",
          all("cache_control" not in b for b in system_blocks([Message(role="system", content="V")])))
    check("no system message → None", system_blocks([Message(role="user", content="x")]) is None)
    # cache-aware pricing on the real manifest (claude-sonnet-4-6: in 3.0, read 0.3, write 3.75)
    naive = pricing.estimate_cost_usd("claude-sdk", "claude-sonnet-4-6", 1000, 0)
    read = pricing.estimate_cost_usd("claude-sdk", "claude-sonnet-4-6", 0, 0, cache_read=1000)
    write = pricing.estimate_cost_usd("claude-sdk", "claude-sonnet-4-6", 0, 0, cache_creation=1000)
    check("cache read ≈ 0.1× input", abs(read - naive * 0.1) < 1e-9)
    check("cache write ≈ 1.25× input", abs(write - naive * 1.25) < 1e-9)


def _stream() -> None:
    from alphaforge_anton_llm.providers._claude_stream import claude_stream
    ev = [
        SimpleNamespace(type="message_start", message=SimpleNamespace(usage=SimpleNamespace(
            input_tokens=20, cache_read_input_tokens=480, cache_creation_input_tokens=0))),
        SimpleNamespace(type="content_block_delta", delta=SimpleNamespace(type="text_delta", text="hi")),
        SimpleNamespace(type="message_delta", usage=SimpleNamespace(output_tokens=3)),
    ]

    class FS:
        def __init__(self): self._it = iter(ev)
        def __aiter__(self): return self
        async def __anext__(self):
            try:
                return next(self._it)
            except StopIteration:
                raise StopAsyncIteration
        async def __aenter__(self): return self
        async def __aexit__(self, *_): pass

    class FC:
        class messages:
            @staticmethod
            def stream(**kw): return FS()

    async def run():
        return [s async for s in claude_stream(
            client=FC(), model="claude-sonnet-4-6", provider_name="claude-sdk", kw={})]
    final = asyncio.run(run())[-1]
    check("stream carries cache_read_input_tokens", final.cache_read_input_tokens == 480)
    check("stream carries cache_creation_input_tokens", final.cache_creation_input_tokens == 0)


def _prompt_marking() -> None:
    from app.modules.concierge import prompt_service as ps
    req = MagicMock(provider="auto", model_id=None, auto_level="auto")
    req.messages = [SimpleNamespace(role="user", content="hello", images=[])]
    reg = MagicMock()
    reg.is_private.return_value = False
    reg.vision_providers.return_value = []
    obj = MagicMock()
    obj.context_text.return_value = "OBJTEXT"
    with patch.object(ps, "fux_recall", AsyncMock(return_value="FUXG")), \
         patch.object(ps, "load_context", AsyncMock(return_value="MEMTEXT")), \
         patch.object(ps, "load_objective", return_value=obj), \
         patch.object(ps, "web_ground", AsyncMock()), \
         patch.object(ps, "signals_ground", AsyncMock()), \
         patch.object(ps, "registry", reg):
        a = asyncio.run(ps.assemble(req))
    cacheable = {m.content for m in a.msgs if m.cacheable}
    check("SYSTEM block marked cacheable", any(m.cacheable and m.role == "system" for m in a.msgs))
    check("objective + memory in cacheable prefix",
          "OBJTEXT" in cacheable and any("MEMTEXT" in c for c in cacheable))
    check("Fux grounding NOT cacheable (volatile)",
          all(not m.cacheable for m in a.msgs if "FUXG" in m.content))
    check("user turn not cacheable", all(not m.cacheable for m in a.msgs if m.role == "user"))


def main() -> int:
    _adapter_and_pricing()
    _stream()
    _prompt_marking()
    print("\n" + ("❌ claude-cache probe FAILED" if _fail
                  else "✅ Phase-3 cache marking, placement, pricing & stream split hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
