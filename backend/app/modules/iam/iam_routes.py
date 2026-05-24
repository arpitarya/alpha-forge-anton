from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, require_owner, user_from_jwt
from app.modules.iam import iam_key_service as keys
from app.modules.iam import iam_service as svc
from app.modules.iam.iam_key_routes import router as key_router
from app.modules.iam.iam_models import IamUser
from app.modules.iam.iam_schemas import (
    AuditEntry,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/iam", tags=["iam"])
router.include_router(key_router)


def _client(request: Request) -> tuple[str | None, str | None]:
    ip = request.client.host if request.client else None
    return ip, request.headers.get("user-agent")


@router.post("/register", response_model=UserResponse)
async def register(req: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip, ua = _client(request)
    count = (await db.execute(select(func.count()).select_from(IamUser))).scalar_one()
    bootstrap = count == 0 or settings.iam_owner_registration_open
    if not bootstrap:
        auth = request.headers.get("Authorization", "")
        if not auth.lower().startswith("bearer "):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
        actor = await user_from_jwt(auth.split(" ", 1)[1].strip(), db)
        if actor.role != "owner":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "owner role required")
    return await svc.register_user(db, req, ip, ua)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip, ua = _client(request)
    _, access, refresh, expires_in = await svc.login(db, req, ip, ua)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=expires_in)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip, ua = _client(request)
    access, raw, expires_in = await svc.refresh_tokens(db, req.refresh_token, ip, ua)
    return TokenResponse(access_token=access, refresh_token=raw, expires_in=expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    req: RefreshRequest,
    request: Request,
    user: IamUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _client(request)
    await svc.logout(db, req.refresh_token, user.id, ip, ua)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
async def me(user: IamUser = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[UserResponse])
async def list_users(_: IamUser = Depends(require_owner), db: AsyncSession = Depends(get_db)):
    return await keys.list_users(db)


@router.get("/audit", response_model=list[AuditEntry])
async def audit(_: IamUser = Depends(require_owner), db: AsyncSession = Depends(get_db)):
    return await keys.list_audit(db)
