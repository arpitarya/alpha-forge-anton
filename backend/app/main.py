"""FastAPI application factory."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import get_logger, setup_logging
from app.modules import api_router
from app.modules.brokers.refetch import start_refetch_loop
from app.modules.brokers.registry import SOURCES

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("AlphaForge starting up (env=%s)", settings.app_env)
    refetch_task = await start_refetch_loop(SOURCES)
    yield
    refetch_task.cancel()
    with suppress(asyncio.CancelledError):
        await refetch_task
    logger.info("AlphaForge shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-powered financial analysis & trading platform for Indian markets",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS — origins locked down; methods/headers explicit
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    # Routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
