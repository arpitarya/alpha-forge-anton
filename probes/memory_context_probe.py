"""Standing-context injection probe — asserts load_context() concatenates all
MEMORY_DOCS (best-effort per doc) and degrades cleanly when elgar is absent.

Standalone (no CDP, no elgar). Run:  just probe memory-context
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def main() -> int:
    from app.modules.concierge.memory_service import (
        CONTEXT_MAX,
        MEMORY_DOCS,
        MEMORY_PREAMBLE,
        load_context,
    )

    fake = {doc: f"Fake content for {doc}." for doc in MEMORY_DOCS}

    async def _fake_get(doc_id: str, collection: str | None = None) -> str | None:
        return fake.get(doc_id)

    # 1. All docs present — result must contain each doc's section header + body text
    with patch("app.modules.plans.elgar_bridge.get", side_effect=_fake_get):
        result = asyncio.run(load_context())

    expected_docs = list(MEMORY_DOCS)
    check(
        "all expected docs present",
        expected_docs == ["investor-profile", "trading-sleeve-rules",
                          "hard-exclusion-list", "portfolio-snapshot", "orff-context"],
    )
    for doc in MEMORY_DOCS:
        check(f"load_context includes '{doc}' header", f"## {doc}" in result)
        check(f"load_context includes '{doc}' body", f"Fake content for {doc}" in result)
    check("result within CONTEXT_MAX", len(result) <= CONTEXT_MAX, f"{len(result)} > {CONTEXT_MAX}")

    # 2. One doc missing — best-effort: others still present, no exception
    missing = "investor-profile"
    partial_fake = {k: v for k, v in fake.items() if k != missing}

    async def _partial_get(doc_id: str, collection: str | None = None) -> str | None:
        return partial_fake.get(doc_id)

    with patch("app.modules.plans.elgar_bridge.get", side_effect=_partial_get):
        partial = asyncio.run(load_context())

    check(f"missing doc '{missing}' omitted (best-effort)", f"## {missing}" not in partial)
    for doc in MEMORY_DOCS:
        if doc != missing:
            check(f"other doc still present after skip ({doc})", f"## {doc}" in partial)

    # 3. All docs raise — result is empty string, no exception propagates
    async def _raise_get(doc_id: str, collection: str | None = None) -> str | None:
        raise RuntimeError("elgar unavailable")

    with patch("app.modules.plans.elgar_bridge.get", side_effect=_raise_get):
        try:
            empty = asyncio.run(load_context())
            check("all-fail degrades to empty string (no exception)", empty == "", repr(empty))
        except Exception as exc:
            check("all-fail degrades to empty string (no exception)", False, f"raised {exc!r}")

    # 4. MEMORY_PREAMBLE is non-empty (prompt_service wraps context with it)
    check("MEMORY_PREAMBLE is non-empty", bool(MEMORY_PREAMBLE.strip()))

    print("\n" + ("❌ memory-context probe FAILED" if _fail else "✅ load_context injection guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
