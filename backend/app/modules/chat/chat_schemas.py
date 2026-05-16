"""Request/response schemas for the Alpha chat endpoint."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


ModelSlug = Literal[
    "auto", "gemini", "groq", "claude-sdk", "cerebras", "mistral", "openrouter", "huggingface"
]


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: ModelSlug = "auto"


# Provider slug → QueryType slug (for explicit provider selection)
PROVIDER_TO_QUERY_TYPE: dict[str, str] = {
    "claude-sdk":   "investment_plan",
    "openrouter":   "investment_plan",
    "gemini":       "investment_plan",
    "groq":         "factoid",
    "cerebras":     "factoid",
    "mistral":      "factoid",
    "huggingface":  "factoid",
}
