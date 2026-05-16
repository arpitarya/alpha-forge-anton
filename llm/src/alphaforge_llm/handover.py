"""Handover — context bridge when the active provider switches mid-session."""

from __future__ import annotations

import logging

from alphaforge_llm.types import Message

logger = logging.getLogger(__name__)

# Never summarise fewer than this many trailing turns.
_MIN_RAW_TURNS = 8

# Estimated chars-per-token; used to gauge window overflow without a real tokeniser.
_CHARS_PER_TOKEN = 4


def _estimate_tokens(messages: list[Message]) -> int:
    return sum(len(m.content) for m in messages) // _CHARS_PER_TOKEN


class Handover:
    """Reconstructs the conversation for a new provider, trimming if needed."""

    def __init__(self, context_limit_tokens: int = 4096) -> None:
        self._limit = context_limit_tokens

    def prepare(self, messages: list[Message]) -> list[Message]:
        if _estimate_tokens(messages) <= self._limit:
            return messages

        system = [m for m in messages if m.role == "system"]
        turns = [m for m in messages if m.role != "system"]

        # Always keep the last _MIN_RAW_TURNS turns verbatim.
        recent = turns[-_MIN_RAW_TURNS:]
        older = turns[:-_MIN_RAW_TURNS]

        if not older:
            return system + recent

        summary_text = self._summarise(older)
        summary_msg = Message(role="user", content=f"[Context summary]\n{summary_text}")
        result = system + [summary_msg] + recent
        logger.info(
            "Handover: summarised %d older turns → %d tokens",
            len(older), _estimate_tokens(result),
        )
        return result

    def _summarise(self, messages: list[Message]) -> str:
        lines = []
        for m in messages:
            prefix = "User" if m.role == "user" else "Assistant"
            lines.append(f"{prefix}: {m.content[:200]}")
        return "\n".join(lines)
