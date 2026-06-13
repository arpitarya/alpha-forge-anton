"""Concierge routes — SSE chat streaming and STT transcription."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user
from app.modules.concierge.compose_schemas import ComposeRequest, ComposeResponse
from app.modules.concierge.compose_service import compose
from app.modules.concierge.concierge_schemas import ChatRequest, MemoryDoc
from app.modules.concierge.concierge_service import stream_chat
from app.modules.concierge.memory_service import load_memory, save_memory
from app.modules.concierge.stt_service import transcribe

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/compose")
async def compose_ui(body: ComposeRequest) -> ComposeResponse:
    """Generate a validated UISpec the client can safely render (§18.3)."""
    return await compose(body)


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


@router.get("/memory")
async def get_memory() -> MemoryDoc:
    """The user-editable context doc Orff injects into every chat."""
    return MemoryDoc(content=await load_memory())


@router.put("/memory")
async def put_memory(body: MemoryDoc) -> MemoryDoc:
    return MemoryDoc(content=await save_memory(body.content))
