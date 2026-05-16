"""1-pager LLM tester. Run: uv run --with fastapi --with uvicorn --with python-dotenv \\
  python -m llm.playground.server   (from repo root)
Then open http://localhost:8765
"""
from __future__ import annotations

import sys, time, asyncio
from pathlib import Path

import yaml
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


EVAL_FILE = ROOT / "llm" / "eval" / "eval_suite.yaml"


# Providers with strict free-tier rate limits need a pause between requests.
_EVAL_DELAY: dict[str, float] = {"openrouter": 15.0, "cerebras": 4.0}


class EvalIn(BaseModel):
    provider: str
    case_id: str | None = None  # None = run all


@app.get("/eval/cases")
async def eval_cases() -> dict:
    data = yaml.safe_load(EVAL_FILE.read_text())
    return {"cases": data["cases"]}


@app.post("/eval/run")
async def eval_run(req: EvalIn) -> JSONResponse:
    data = yaml.safe_load(EVAL_FILE.read_text())
    cases = data["cases"]
    if req.case_id:
        cases = [c for c in cases if c["id"] == req.case_id]
    if not cases:
        return JSONResponse({"error": "no matching cases"}, status_code=400)

    adapter = REGISTRY.get(req.provider)
    if adapter is None:
        return JSONResponse({"error": f"unknown provider {req.provider}"}, status_code=400)

    delay = _EVAL_DELAY.get(req.provider, 0.0)
    results = []
    for i, c in enumerate(cases):
        if i > 0 and delay:
            await asyncio.sleep(delay)
        msgs = [Message(role="user", content=c["question"])]
        t0 = time.time()
        try:
            r = await adapter.complete(msgs)
            answer = r.content or ""
            latency = int((time.time() - t0) * 1000)
            kw_hits = [k for k in c.get("expected_keywords", []) if k.lower() in answer.lower()]
            contains = c.get("expected_contains_any", [])
            any_hits = [k for k in contains if k.lower() in answer.lower()]
            passed = len(any_hits) > 0 if c.get("expected_contains_any") else True
            results.append({
                "id": c["id"], "category": c["category"],
                "question": c["question"], "rubric": c.get("rubric", ""),
                "answer": answer, "latency_ms": latency,
                "model": r.model,
                "keyword_hits": kw_hits,
                "any_hits": any_hits,
                "passed": passed,
            })
        except Exception as exc:
            results.append({
                "id": c["id"], "category": c["category"],
                "question": c["question"], "rubric": c.get("rubric", ""),
                "answer": "", "latency_ms": int((time.time() - t0) * 1000),
                "model": "", "keyword_hits": [], "any_hits": [],
                "passed": False, "error": f"{type(exc).__name__}: {exc}",
            })
    return JSONResponse({"results": results})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
