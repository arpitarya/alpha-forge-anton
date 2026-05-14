"""LLM Gateway endpoints — multi-provider AI completion.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.core.logging import get_logger
from app.modules.llm.benchmark_routes import router as benchmark_router
from app.modules.llm.llm_schemas import (
    AnalyzeRequest,
    CompleteRequest,
    LLMResponseModel,
)
from app.modules.llm.llm_service import get_gateway

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger("routes.llm")


def _to_response(r) -> LLMResponseModel:
    return LLMResponseModel(
        content=r.content, model=r.model, provider=r.provider.value,
        tokens_used=r.tokens_used, latency_ms=r.latency_ms, cost=r.cost,
    )


@router.post("/complete", response_model=LLMResponseModel)
@limiter.limit("20/minute")
async def complete(request: Request, body: CompleteRequest):
    from alphaforge_llm_gateway.types import LLMProvider, QueryType

    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    provider = LLMProvider(body.provider) if body.provider else None
    logger.info("LLM complete: type=%s, provider=%s", body.query_type, body.provider)
    response = await get_gateway().complete(
        QueryType(body.query_type), messages,
        provider=provider, model=body.model,
        temperature=body.temperature, max_tokens=body.max_tokens,
    )
    return _to_response(response)


@router.post("/analyze-screener", response_model=LLMResponseModel)
@limiter.limit("10/minute")
async def analyze_screener(request: Request, body: AnalyzeRequest):
    logger.info("LLM analyze-screener: %d chars", len(body.raw_output))
    return _to_response(await get_gateway().analyze_screener(body.raw_output))


@router.post("/explain-picks", response_model=LLMResponseModel)
@limiter.limit("10/minute")
async def explain_picks(request: Request, body: AnalyzeRequest):
    logger.info("LLM explain-picks: %d chars", len(body.raw_output))
    return _to_response(await get_gateway().explain_picks(body.raw_output))


@router.get("/providers")
async def list_providers():
    return await get_gateway().providers_status()


router.include_router(benchmark_router, prefix="/benchmark")
