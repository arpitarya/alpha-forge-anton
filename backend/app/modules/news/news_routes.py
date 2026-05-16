"""News API endpoints.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user
from app.core.logging import get_logger
from app.modules.news.news_schemas import NewsItemResponse, NewsSearchRequest, SourceStatusResponse
from app.modules.news.news_service import get_aggregator

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger("routes.news")


@router.get("/news/search", response_model=list[NewsItemResponse])
async def search_news(
    q: str = Query(..., description="Search query — company, topic, or NSE ticker"),
    symbols: str = Query(default="", description="Comma-separated NSE tickers e.g. RELIANCE,TCS"),
    limit: int = Query(default=20, ge=1, le=50),
) -> list[NewsItemResponse]:
    """Search Indian market news across all enabled sources."""
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    agg = get_aggregator()
    items = await agg.search(q, symbols=symbol_list or None, limit=limit)
    logger.debug("news search q=%r symbols=%r → %d results", q, symbol_list, len(items))
    return [NewsItemResponse(**item.model_dump()) for item in items]


@router.post("/news/search", response_model=list[NewsItemResponse])
async def search_news_post(req: NewsSearchRequest) -> list[NewsItemResponse]:
    """Search news — POST variant for richer filters (since, symbol list)."""
    agg = get_aggregator()
    items = await agg.search(
        req.q,
        symbols=req.symbols or None,
        since=req.since,
        limit=req.limit,
    )
    return [NewsItemResponse(**item.model_dump()) for item in items]


@router.get("/news/sources", response_model=list[SourceStatusResponse])
async def list_sources() -> list[SourceStatusResponse]:
    """Health and quota status for every registered news source."""
    agg = get_aggregator()
    statuses = await agg.health()
    return [SourceStatusResponse(**s.model_dump()) for s in statuses]
