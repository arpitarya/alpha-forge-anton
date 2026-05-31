"""Concierge routes — SSE streaming endpoint for the Orff concierge rail."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user
from app.modules.concierge.concierge_schemas import ChatRequest
from app.modules.concierge.concierge_service import stream_chat

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/")
async def concierge(body: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_chat(body),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
