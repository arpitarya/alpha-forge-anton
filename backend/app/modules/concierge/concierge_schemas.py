"""Request/response schemas for the Orff concierge endpoint."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


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


# Provider slug -> default QueryType slug (used for chain selection when the
# user is on Auto / provider-Auto and the gateway picks the chain).
PROVIDER_TO_QUERY_TYPE: dict[str, str] = {
    "claude-sdk":   "investment_plan",
    "openrouter":   "investment_plan",
    "gemini":       "portfolio_overview",
    "mistral":      "investment_plan",
    "groq":         "factoid",
    "cerebras":     "factoid",
    "huggingface":  "factoid",
}
