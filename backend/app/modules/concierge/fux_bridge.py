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
    """Composable vocabulary: solar-ui components + the repo's data hooks.

    Components are scoped to `packages/solar-ui` (composition never reaches feature
    components); hooks come from the whole repo — both then narrowed to the curated
    sets in `compose_registry` so prompt = validator = client whitelist."""
    code, out = await _run("components", "--scope", "packages/solar-ui", "--json")
    if code != 0:
        raise RuntimeError(f"fux components failed: {out[:200]}")
    scoped = json.loads(out)
    code, out = await _run("components", "--json")
    if code != 0:
        raise RuntimeError(f"fux components failed: {out[:200]}")
    scoped["hooks"] = json.loads(out).get("hooks", [])
    return scoped


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


async def critic_suggestions(proposal: str) -> list[str]:
    """Advisory judgment layer for the runtime critic (`runtime-note-pii`).

    Runs `fux critic "<proposal>"` and returns its judgment *suggestions* — advisory-first
    (fux ≥ 0.5.0): judgment principles SUGGEST, they do not block here. The deterministic
    money/PII block is enforced in-process by `critic_guard`, never delegated to this.
    Best-effort: returns [] on any failure so a chat write never breaks on the advisory pass.
    Any tokens a host-agent self-critique spends are metered by Cage at the LLM gateway."""
    try:
        code, out = await _run("critic", proposal)
        if code not in (0, 2):
            return []
        # Surface advisory judgment lines: `· [needs-judgment] <id>: …` / `(advisory)`.
        return [ln.strip() for ln in out.splitlines()
                if "needs-judgment" in ln or "(advisory)" in ln]
    except Exception:  # advisory is additive — never block a write
        return []
