"""news module — public API surface."""

from __future__ import annotations

from app.modules.news.news_routes import router

__all__ = ["router"]
