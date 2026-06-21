"""Request/response schemas for the Orff concierge endpoint."""

from __future__ import annotations

from typing import Literal, get_args

from alphaforge_anton_llm import registry
from pydantic import BaseModel, Field, field_validator

# Vision attachments: data URLs, capped so a paste can't balloon the request.
MAX_IMAGES = 4
MAX_IMAGE_CHARS = 6_000_000  # ~4.5 MB binary as base64


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    images: list[str] = Field(default_factory=list, max_length=MAX_IMAGES)

    @field_validator("images")
    @classmethod
    def _image_size(cls, v: list[str]) -> list[str]:
        if any(len(img) > MAX_IMAGE_CHARS for img in v):
            raise ValueError(f"image exceeds {MAX_IMAGE_CHARS} chars (base64)")
        return v


class MemoryDoc(BaseModel):
    """The user-editable context document shown in the Memory panel."""

    content: str = ""


# Conversation history — persisted to elgar, one doc per session (history_service).
MAX_SESSION_TURNS = 200


class SessionTurn(BaseModel):
    """One exchange in a saved conversation (the resume-critical fields only)."""

    query: str
    response: str = ""
    provider: str | None = None
    model: str | None = None


class SessionMeta(BaseModel):
    """A conversation's sidebar entry."""

    id: str
    title: str = ""


class SessionDoc(SessionMeta):
    """A conversation loaded for resume — its turns plus the sidebar meta."""

    turns: list[SessionTurn] = Field(default_factory=list)


class SaveSessionBody(BaseModel):
    """PUT body for /history/{id} — the session id comes from the path."""

    title: str = ""
    turns: list[SessionTurn] = Field(default_factory=list, max_length=MAX_SESSION_TURNS)


# Pydantic needs a static type, so the slugs are spelled out — but they must mirror
# the registry manifest (single source of truth). The assertion below fails loudly
# at import if a provider is added/removed there without updating this Literal.
ProviderSlug = Literal[
    "auto",
    "gemini",
    "groq",
    "cerebras",
    "mistral",
    "openrouter",
    "huggingface",
    "claude-sdk",
]

assert set(get_args(ProviderSlug)) == registry.provider_slugs() | {"auto"}, (
    "ProviderSlug drifted from registry/providers.json — "
    "regenerate after editing the manifest (see concierge-registry-single-source)"
)

AutoLevel = Literal["top", "provider", "none"]
# "Think harder" override (trusted lane). Auto = intent routing decides; On = force
# adaptive thinking on the intent's model; Off = disable it. See Phase 4.
ThinkingMode = Literal["auto", "on", "off"]
# Agent-initiated deep search (replaces the web_grounding toggle): Auto asks via a
# confirm card, Always runs cardless, Never doesn't offer the tool. See the handoff.
DeepSearchMode = Literal["auto", "always", "never"]


class ChatRequest(BaseModel):
    """
    Resolved model choice from the frontend ModelPicker.

    The frontend already applies its routing heuristic, so the backend receives
    a concrete provider when the user is not on top-level Auto. `auto_level`
    documents how the choice was made and is preserved for telemetry.
    """

    messages: list[ChatMessage]
    provider: ProviderSlug = "auto"
    model_id: str | None = None
    auto_level: AutoLevel = "top"
    # Agent-initiated, confirm-gated Parallel deep search. Auto (default) = Orff asks
    # before spending; the free RSS/NSE/yfinance path stays the everyday default.
    deep_search_mode: DeepSearchMode = "auto"
    # "Think harder" override; Auto defers to intent routing (the default behaviour).
    thinking_mode: ThinkingMode = "auto"
    # Volatile, single-turn web grounding resent when a deep-search card is approved, so Orff
    # answers instead of re-asking (injected uncached by prompt_service; never persisted).
    grounding: str | None = None
