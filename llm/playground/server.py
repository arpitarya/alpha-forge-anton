"""1-pager LLM tester. Run: uv run --with fastapi --with uvicorn --with python-dotenv \\
  python -m llm.playground.server   (from repo root)
Then open http://localhost:8765
"""
from __future__ import annotations

import sys, time, asyncio
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "llm" / "src"))
for f in (".env", ".env.local", ".env.cred.local"):
    p = ROOT / f
    if p.exists():
        load_dotenv(p, override=True)

from alphaforge_llm import REGISTRY, Message  # noqa: E402

HTML = (Path(__file__).parent / "index.html").read_text()

app = FastAPI(title="alphaforge-llm playground")


class CompleteIn(BaseModel):
    provider: str
    prompt: str
    system: str | None = None


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return HTML


@app.get("/providers")
async def providers() -> dict:
    healths = await asyncio.gather(*(a.health() for a in REGISTRY.values()))
    return {
        "providers": [
            {"name": n, "model": a.default_model(), "available": h.available,
             "error": h.last_error}
            for (n, a), h in zip(REGISTRY.items(), healths, strict=True)
        ]
    }


@app.post("/complete")
async def complete(req: CompleteIn) -> JSONResponse:
    adapter = REGISTRY.get(req.provider)
    if adapter is None:
        return JSONResponse({"error": f"unknown provider {req.provider}"}, status_code=400)
    msgs = []
    if req.system:
        msgs.append(Message(role="system", content=req.system))
    msgs.append(Message(role="user", content=req.prompt))
    t0 = time.time()
    try:
        r = await adapter.complete(msgs)
        return JSONResponse({
            "ok": True,
            "provider": r.provider,
            "model": r.model,
            "content": r.content,
            "prompt_tokens": r.prompt_tokens,
            "completion_tokens": r.completion_tokens,
            "latency_ms": int((time.time() - t0) * 1000),
        })
    except Exception as exc:
        return JSONResponse({
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "latency_ms": int((time.time() - t0) * 1000),
        }, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
