"""FastAPI dependencies — shared across all route modules."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token

try:
    from posture import decide, engine as posture_engine
    from posture.policy_engine import PostureRules
    from posture.step_up import Action
    from app.core.paths import resolve as _resolve_path
    _POSTURE_YAML = _resolve_path("DANTE_POSTURE_YAML", "dante", "posture.yaml")
    _posture_rules = PostureRules.load(_POSTURE_YAML) if _POSTURE_YAML.exists() else None
    _POSTURE = _posture_rules is not None
except ImportError:
    _POSTURE = False
    _posture_rules = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/iam/login", auto_error=False)

UNAUTHORIZED = HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")


@dataclass
class UserClaims:
    """Lightweight user object built from Wagner JWT claims — no DB round-trip."""
    id: uuid.UUID        # Wagner guid (== JWT sub)
    role: str
    email: str
    is_active: bool = field(default=True)


def user_from_jwt(token: str) -> UserClaims:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UNAUTHORIZED
    try:
        uid = uuid.UUID(payload["sub"])
    except (ValueError, AttributeError):
        raise UNAUTHORIZED
    return UserClaims(
        id=uid,
        role=payload.get("role", "viewer"),
        email=payload.get("email", ""),
    )


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
) -> UserClaims:
    if not token:
        raise UNAUTHORIZED
    user = user_from_jwt(token)
    if _POSTURE and _posture_rules is not None:
        score = posture_engine().score(str(user.id))
        action = decide(score, request.url.path, _posture_rules)
        if action == Action.STEP_UP:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "TOTP required")
        if action == Action.BLOCK:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "blocked")
    return user


def require_owner(user: UserClaims = Depends(get_current_user)) -> UserClaims:
    if user.role != "owner":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "owner role required")
    return user
