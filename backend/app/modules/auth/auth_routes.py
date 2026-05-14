"""Auth endpoints — token login only."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, verify_password

router = APIRouter()

_INVALID = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != settings.admin_username:
        raise _INVALID
    if not verify_password(form_data.password, settings.admin_password_hash):
        raise _INVALID
    return {
        "access_token": create_access_token(form_data.username),
        "token_type": "bearer",
    }
