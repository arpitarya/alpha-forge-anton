"""Provider registry — auto-populated at import."""

from __future__ import annotations

from alphaforge_anton_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_anton_llm.providers.cerebras import CerebrasAdapter
from alphaforge_anton_llm.providers.claude_sdk import ClaudeSdkAdapter
from alphaforge_anton_llm.providers.gemini import GeminiAdapter
from alphaforge_anton_llm.providers.groq import GroqAdapter
from alphaforge_anton_llm.providers.huggingface import HuggingFaceAdapter
from alphaforge_anton_llm.providers.mistral import MistralAdapter
from alphaforge_anton_llm.providers.openrouter import OpenRouterAdapter

REGISTRY: dict[str, ProviderAdapter] = {
    "gemini":      GeminiAdapter(),
    "groq":        GroqAdapter(),
    "openrouter":  OpenRouterAdapter(),
    "huggingface": HuggingFaceAdapter(),
    "cerebras":    CerebrasAdapter(),
    "mistral":     MistralAdapter(),
    "claude-sdk":  ClaudeSdkAdapter(),
}

__all__ = [
    "REGISTRY",
    "ProviderAdapter",
    "ProviderHealth",
    "CerebrasAdapter",
    "ClaudeSdkAdapter",
    "GeminiAdapter",
    "GroqAdapter",
    "HuggingFaceAdapter",
    "MistralAdapter",
    "OpenRouterAdapter",
]
