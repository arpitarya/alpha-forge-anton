"""SSE wire helpers for the Orff stream — event framing, secret redaction, and
the <think> reasoning split emitted by free reasoning models (deepseek/qwq-style).

Every event is one JSON object per `data:` line; the event vocabulary is
documented in concierge/README.md (token snapshot, tool, thinking, followups,
confirm, spec, error, [DONE])."""

from __future__ import annotations

import json
import re

# Upstream provider errors embed the request URL, which carries the API key as a
# `?key=…`/`?api_key=…` query param. Never forward a live secret to the browser.
_SECRET_RE = re.compile(r"(?i)([?&](?:api[_-]?key|key|token|access_token)=)[^&\s\"']+")

# A tool call emitted as TEXT (not a tool_use block) leaks raw <invoke>/<parameter> markup.
_TOOL_MARKUP_RE = re.compile(r"<\s*/?\s*(?:antml:)?(?:invoke|parameter)\b[^>]*>", re.IGNORECASE)

_THINK_OPEN = "<think>"
_THINK_CLOSE = "</think>"


def sse(payload: dict) -> bytes:
    return f"data: {json.dumps(payload)}\n\n".encode()


def redact(msg: str) -> str:
    return _SECRET_RE.sub(r"\1<redacted>", msg)


def strip_tool_markup(text: str) -> str:
    """Drop leaked tool-call tags so they never persist into a turn (the kreglqek leak)."""
    return _TOOL_MARKUP_RE.sub("", text).strip() if text else text


def split_thinking(content: str) -> tuple[str, str]:
    """Split a `<think>…</think>` reasoning trace from the visible answer.

    Snapshots are cumulative, so the close tag may not have streamed yet — an
    unclosed block means everything so far is reasoning and the answer is empty.
    Returns (thinking, visible); non-reasoning models pass through unchanged.
    """
    stripped = content.lstrip()
    if not stripped.startswith(_THINK_OPEN):
        return "", content
    body = stripped[len(_THINK_OPEN) :]
    if _THINK_CLOSE in body:
        thinking, visible = body.split(_THINK_CLOSE, 1)
        return thinking.strip(), visible.lstrip()
    return body.strip(), ""
