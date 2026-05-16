"""API module registry — every feature module mounts its router here."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.auth import router as auth_router
from app.modules.chat import router as chat_router
from app.modules.dashboard import router as dashboard_router
from app.modules.health import router as health_router
from app.modules.news import router as news_router
from app.modules.portfolio import router as portfolio_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(news_router, tags=["news"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

__all__ = ["api_router"]
