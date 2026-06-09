"""Schemas for Orff on-the-fly component composition (§18.3)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ComposeRequest(BaseModel):
    prompt: str
    provider: str = "auto"


class ComposeResponse(BaseModel):
    """A validated UISpec (or the violations that rejected it). `spec` is a tree of
    registry components — declarative, never code — safe for the client to render."""

    spec: dict[str, Any] | None
    valid: bool
    errors: list[str] = []
    provider: str | None = None
    model: str | None = None
    attempts: int = 1
