"""FastAPI dependencies — shared across all route modules."""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token

try:
    from posture import decide, engine as posture_engine
    from posture.policy_engine import PostureRules
    from posture.step_up import Action
    from pathlib import Path as _Path
    _POSTURE_YAML = _Path("~/.alphaforge-anton/dante/posture.yaml").expanduser()
    _posture_rules = PostureRules.load(_POSTURE_YAML) if _POSTURE_YAML.exists() else None
    _POSTURE = _posture_rules is not None
except ImportError:
    _POSTURE = False
    _posture_rules = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/iam/login", auto_error=False)

UNAUTHORIZED = HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")


async def user_from_jwt(token: str, db: AsyncSession):
    from app.modules.iam.iam_key_service import get_user_by_id
    from app.modules.iam.iam_models import IamUser  # noqa: F401

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UNAUTHORIZED
    user = await get_user_by_id(db, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise UNAUTHORIZED
    return user


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.iam.iam_utils import API_KEY_PREFIX
    from app.modules.iam.iam_key_service import authenticate_api_key

    if not token:
        raise UNAUTHORIZED

    if token.startswith(API_KEY_PREFIX):
        user = await authenticate_api_key(db, token)
        if user is None:
            raise UNAUTHORIZED
    else:
        user = await user_from_jwt(token, db)

    if _POSTURE and _posture_rules is not None:
        score = posture_engine().score(str(user.id))
        action = decide(score, request.url.path, _posture_rules)
        if action == Action.STEP_UP:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "TOTP required")
        if action == Action.BLOCK:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "blocked")

    return user


def require_owner(user=Depends(get_current_user)):
    if user.role != "owner":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "owner role required")
    return user
