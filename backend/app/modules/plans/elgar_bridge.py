"""Bridge to the elgar plan store — the elgar CLI is Anton's ONLY door to it.

Anton owns no elgar path; elgar maintains the store + path. Writes go through
`save` (git-committed; a bad/unreachable store raises `ElgarStoreError`, never a
silent local fallback); reads through `get`/`get_sync` (memoised for hot loaders).
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_read_cache: dict[tuple[str, str | None], str | None] = {}  # sync reads; cleared by `save`


class ElgarStoreError(RuntimeError):
    """An elgar write could not reach a valid store — fail loud, never write elsewhere."""


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


def _dir(collection: str | None) -> list[str]:
    return ["--dir", collection] if collection else []


async def save(
    plan_id: str, content: str, message: str | None = None, collection: str | None = None
) -> str:
    """Write a doc into the store; returns its `elgar://plan/<id>` ref."""
    args = ["save", plan_id, *_dir(collection)] + (["-m", message] if message else [])
    code, out = await _run(*args, stdin=content.encode())
    if code != 0:  # elgar self-validates its store; a bad/unreachable store fails loud here
        raise ElgarStoreError(f"elgar save failed (store unreachable/invalid): {out[:200]}")
    _read_cache.pop((plan_id, collection), None)
    return f"elgar://plan/{plan_id}"


def get_sync(doc_id: str, collection: str | None = None) -> str | None:
    """Cached sync read via the elgar CLI (memoised; cleared on save). None when absent."""
    if (key := (doc_id, collection)) not in _read_cache:
        try:
            p = subprocess.run(  # noqa: S603
                [_bin(), "get", doc_id, *_dir(collection)], capture_output=True, text=True
            )
            _read_cache[key] = p.stdout if p.returncode == 0 else None
        except OSError:
            _read_cache[key] = None
    return _read_cache[key]


async def get(doc_id: str, collection: str | None = None) -> str | None:
    """Read a doc's content from the store; None when it does not exist."""
    code, out = await _run("get", doc_id, *_dir(collection))
    return out if code == 0 else None


async def list_docs(prefix: str = "", collection: str | None = None) -> list[dict]:
    """Docs in a collection (`{id, status, title}`), optionally filtered by id prefix."""
    code, out = await _run("list", "--json", *_dir(collection))
    if code != 0:
        return []
    try:
        rows = json.loads(out)
    except json.JSONDecodeError:
        return []
    return [r for r in rows if r.get("id", "").startswith(prefix)]


async def remove(doc_id: str, collection: str | None = None) -> bool:
    """Delete a doc from the store; True on success, False when it does not exist."""
    code, _ = await _run("rm", doc_id, *_dir(collection))
    return code == 0


async def store_path() -> str:
    code, out = await _run("path")
    if code != 0:
        raise RuntimeError(f"elgar path failed: {out[:200]}")
    return out.strip()
