"""Shared types for the LLM gateway."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class QueryType(str, Enum):
    NEWS_LOOKUP = "news_lookup"
    FACTOID = "factoid"
    PORTFOLIO_OVERVIEW = "portfolio_overview"
    STOCK_PICK = "stock_pick"
    INVESTMENT_PLAN = "investment_plan"
    INDUSTRY_NEWS = "industry_news"
    MULTI_TURN = "multi_turn"


class Message(BaseModel):
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    tool_call_id: str | None = None
    name: str | None = None


class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]


class ToolCall(BaseModel):
    call_id: str
    name: str
    args: dict[str, Any]


class ProviderResponse(BaseModel):
    content: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    tool_calls: list[ToolCall] = []
    raw: dict[str, Any] = {}


class EscalationRequest(BaseModel):
    query_summary: str
    messages: list[Message]
    est_tokens: int
    confirmed: bool = False
