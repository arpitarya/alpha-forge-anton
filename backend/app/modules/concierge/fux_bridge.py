"""Bridge to the Fux brain — calls the `fux` CLI for the component registry and
UISpec validation (the §18.3 runtime guardrail). Subprocess, not import, so Orff
talks to the same brain Claude Code does, across venvs. $0, deterministic."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import shutil
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]


def _bin() -> str:
    return os.environ.get("FUX_BIN") or shutil.which("fux") or "fux"


async def _run(*args: str, stdin: bytes | None = None) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        _bin(), *args, cwd=str(_REPO),
        stdin=asyncio.subprocess.PIPE if stdin is not None else None,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate(input=stdin)
    return (proc.returncode or 0), (out.decode() or err.decode())


async def registry() -> dict:
    code, out = await _run("components", "--json")
    if code != 0:
        raise RuntimeError(f"fux components failed: {out[:200]}")
    return json.loads(out)


async def validate(spec: dict) -> tuple[bool, list[str]]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(spec, f)
        tmp = f.name
    try:
        _code, out = await _run("validate-spec", "--json", tmp)
        data = json.loads(out)
        return bool(data["ok"]), list(data["errors"])
    finally:
        os.unlink(tmp)


async def recall(prompt: str, *, max_chars: int = 2000) -> str:
    """Retrieve project knowledge (rules / glossary / memory) relevant to a user
    prompt — the §18 runtime grounding for Orff's replies, same brain Claude Code
    queries. Best-effort: returns "" on any failure so chat never breaks."""
    try:
        code, out = await _run("hook-recall", stdin=json.dumps({"prompt": prompt}).encode())
        text = out.strip()
        return text[:max_chars] if code == 0 and text else ""
    except Exception:  # grounding is additive — never block a reply
        return ""


async def record_feedback(outcome: dict) -> None:
    """Append a compose outcome to the brain's learning loop (§18.4). Best-effort."""
    with contextlib.suppress(Exception):  # telemetry must never break a response
        await _run("feedback", "--record", "-", stdin=json.dumps(outcome).encode())
