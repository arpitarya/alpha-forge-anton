"""Bridge to the elgar plan store — subprocess, same pattern as `fux_bridge`.

Saving goes through the `elgar` CLI so Anton and the operator share one write
path (one git commit per save, store stays outside any public work tree).
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(title: str) -> str:
    return _SLUG_RE.sub("-", title.lower()).strip("-")[:48] or "untitled-plan"


def _bin() -> str:
    return os.environ.get("ELGAR_BIN") or shutil.which("elgar") or "elgar"


async def _run(*args: str, stdin: bytes | None = None) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        _bin(), *args,
        stdin=asyncio.subprocess.PIPE if stdin is not None else None,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate(input=stdin)
    return (proc.returncode or 0), (out.decode() or err.decode())


async def save(plan_id: str, content: str, message: str | None = None) -> str:
    """Write a plan doc into the store; returns its `elgar://plan/<id>` ref."""
    args = ["save", plan_id] + (["-m", message] if message else [])
    code, out = await _run(*args, stdin=content.encode())
    if code != 0:
        raise RuntimeError(f"elgar save failed: {out[:200]}")
    return f"elgar://plan/{plan_id}"


async def get(doc_id: str) -> str | None:
    """Read a doc's content from the store; None when it does not exist."""
    code, out = await _run("get", doc_id)
    return out if code == 0 else None


async def list_docs(prefix: str = "") -> list[dict]:
    """All store docs (`{id, status, title}`), optionally filtered by id prefix."""
    code, out = await _run("list", "--json")
    if code != 0:
        return []
    try:
        rows = json.loads(out)
    except json.JSONDecodeError:
        return []
    return [r for r in rows if r.get("id", "").startswith(prefix)]


async def remove(doc_id: str) -> bool:
    """Delete a doc from the store; True on success, False when it does not exist."""
    code, _ = await _run("rm", doc_id)
    return code == 0


async def store_path() -> str:
    code, out = await _run("path")
    if code != 0:
        raise RuntimeError(f"elgar path failed: {out[:200]}")
    return out.strip()
