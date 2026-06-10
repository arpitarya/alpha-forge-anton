"""Request/response schemas for the Orff concierge endpoint."""

from __future__ import annotations

from typing import Literal, get_args

from alphaforge_anton_llm import registry
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


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
