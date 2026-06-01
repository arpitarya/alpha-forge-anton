"""Speech-to-text via Groq's hosted Whisper (whisper-large-v3-turbo)."""

from __future__ import annotations

import os

import httpx
from fastapi import HTTPException, UploadFile

GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_MODEL = "whisper-large-v3-turbo"
MAX_BYTES = 25 * 1024 * 1024  # Groq's free-tier per-file limit


async def transcribe(audio: UploadFile) -> str:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise HTTPException(503, "STT unavailable: GROQ_API_KEY not configured")

    data = await audio.read()
    if not data:
        raise HTTPException(400, "Empty audio upload")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, f"Audio exceeds {MAX_BYTES // 1024 // 1024} MB limit")

    filename = audio.filename or "audio.webm"
    content_type = audio.content_type or "audio/webm"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            GROQ_STT_URL,
            headers={"Authorization": f"Bearer {key}"},
            files={"file": (filename, data, content_type)},
            data={"model": GROQ_MODEL, "response_format": "json", "language": "en"},
        )

    if resp.status_code != 200:
        raise HTTPException(502, f"STT upstream {resp.status_code}: {resp.text[:200]}")

    return (resp.json().get("text") or "").strip()
