"""API module registry — every feature module mounts its router here."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.concierge import router as concierge_router
from app.modules.dashboard import router as dashboard_router
from app.modules.health import router as health_router
from app.modules.iam import router as iam_router
from app.modules.news import router as news_router
from app.modules.portfolio import router as portfolio_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(iam_router)
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(news_router, tags=["news"])
api_router.include_router(concierge_router, prefix="/concierge", tags=["concierge"])

__all__ = ["api_router"]
