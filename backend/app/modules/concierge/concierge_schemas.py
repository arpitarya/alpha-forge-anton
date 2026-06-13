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
