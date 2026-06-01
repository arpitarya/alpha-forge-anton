"""Concierge routes — SSE chat streaming and STT transcription."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user
from app.modules.concierge.concierge_schemas import ChatRequest
from app.modules.concierge.concierge_service import stream_chat
from app.modules.concierge.stt_service import transcribe

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


@router.post("/stt")
async def stt(file: UploadFile = File(...)) -> dict[str, str]:
    text = await transcribe(file)
    return {"transcript": text}
