"""Parse a Claude Code transcript (`.jsonl`) into a clean `(title, turns)` pair.

Session logs interleave real prose with tool calls, tool results, system reminders,
and slash-command wrappers. This keeps only the human's typed prompts and Claude's
prose replies, so an imported chat reads like a conversation — not a build log.
"""

from __future__ import annotations

import json
from pathlib import Path

# User "text" that is injected context, not something the human actually typed.
_NOISE_PREFIXES = (
    "<system-reminder", "<command-name", "<command-message", "<command-args",
    "<local-command", "<bash-", "<user-prompt", "<ide_", "Caveat:", "[Request interrupted",
)


def _clean(blocks: list) -> str:
    """Join the human/assistant prose in a content array; drop tools, images, noise."""
    out = []
    for b in blocks:
        if not isinstance(b, dict) or b.get("type") != "text":
            continue  # tool_use / tool_result / image → not conversation
        t = (b.get("text") or "").strip()
        if t and not t.startswith(_NOISE_PREFIXES):
            out.append(t)
    return "\n\n".join(out).strip()


def _short_model(m: str | None) -> str | None:
    return m.split("/")[-1] if m else None


def parse(path: Path) -> tuple[str, list[dict]]:
    """`(title, turns)` — turns are `{query, response, provider, model}`.

    Title comes from the transcript's `ai-title` record (falls back to the first
    prompt). Consecutive same-role messages are merged into one turn.
    """
    title = ""
    events: list[tuple[str, str, str | None]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = r.get("type")
        if kind == "ai-title":
            title = (r.get("aiTitle") or "").strip() or title
            continue
        if kind not in ("user", "assistant"):
            continue
        msg = r.get("message") or {}
        content = msg.get("content")
        blocks = content if isinstance(content, list) else [{"type": "text", "text": content}]
        text = _clean(blocks)
        if text:
            events.append((kind, text, msg.get("model")))

    turns: list[dict] = []
    pending: str | None = None
    for role, text, model in events:
        if role == "user":
            pending = f"{pending}\n\n{text}" if pending else text
        else:
            turns.append({
                "query": pending or "",
                "response": text,
                "provider": "claude-code",
                "model": _short_model(model),
            })
            pending = None
    if not title:
        title = (turns[0]["query"][:60] if turns and turns[0]["query"] else "Claude chat")
    return title, turns
