"""Probe every registered LLM provider once and print a one-line result each."""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "llm" / "src"))
for _f in (".env", ".env.local", ".env.cred.local"):
    _p = ROOT / _f
    if _p.exists():
        load_dotenv(_p, override=True)

from alphaforge_anton_llm import REGISTRY, Message  # noqa: E402

PROMPT = [Message(role="user", content="Reply with exactly: pong")]


async def _probe(name: str, adapter) -> None:
    if not os.getenv(adapter.env_key):
        print(f"  {name:<12} SKIP  ({adapter.env_key} not set)")
        return
    if name == "claude-sdk":
        print(f"  {name:<12} SKIP  (paid; gated by CostGuard)")
        return
    t0 = time.time()
    try:
        r = await adapter.complete(PROMPT)
        dt = int((time.time() - t0) * 1000)
        reply = (r.content or "").strip().replace("\n", " ")[:60]
        print(f"  {name:<12} OK    {dt:>5}ms  {r.model:<32}  tok={r.prompt_tokens}+{r.completion_tokens}  {reply!r}")
    except Exception as exc:
        dt = int((time.time() - t0) * 1000)
        print(f"  {name:<12} FAIL  {dt:>5}ms  {type(exc).__name__}: {str(exc)[:120]}")


async def main() -> None:
    print(f"Providers: {list(REGISTRY)}\n")
    for name, adapter in REGISTRY.items():
        await _probe(name, adapter)


if __name__ == "__main__":
    asyncio.run(main())
