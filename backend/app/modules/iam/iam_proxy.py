"""IAM proxy — forwards all /iam/* requests to Wagner."""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Request, Response, status

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter(prefix="/iam", tags=["iam"])
logger = get_logger("routes.iam")

_STRIP_REQ = {"host", "content-length", "transfer-encoding"}
_STRIP_RESP = {"content-encoding", "transfer-encoding", "content-length"}


async def _forward(request: Request, path: str) -> Response:
    url = f"{settings.wagner_url}/api/v1/iam/{path}"
    headers = {k: v for k, v in request.headers.items() if k.lower() not in _STRIP_REQ}
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body(),
            params=request.query_params,
            follow_redirects=False,
        )
    if path == "logout" and resp.status_code >= 400:
        logger.warning("IAM logout proxy returned %s from Wagner", resp.status_code)
        if resp.status_code == status.HTTP_401_UNAUTHORIZED:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in _STRIP_RESP}
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=resp_headers,
        media_type=resp.headers.get("content-type"),
    )


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def iam_proxy(request: Request, path: str = "") -> Response:
    return await _forward(request, path)
