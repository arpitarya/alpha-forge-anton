import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.iam.iam_key_models import IamAuditLog
from app.modules.iam.iam_models import IamRefreshToken, IamUser
from app.modules.iam.iam_schemas import LoginRequest, RegisterRequest
from app.modules.iam.iam_utils import generate_refresh_token, sha256

try:
    from watchman import login_tracker
    from watchman.anomaly_rules import on_failed_login
    _WATCHMAN = True
except ImportError:
    _WATCHMAN = False

INVALID_CREDENTIALS = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")


async def _audit(db, user_id, event, ip, ua, detail=None) -> None:
    db.add(IamAuditLog(user_id=user_id, event=event, ip_address=ip, user_agent=ua, detail=detail))


async def register_user(db: AsyncSession, req: RegisterRequest, ip, ua) -> IamUser:
    user = IamUser(
        email=req.email.lower(),
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        is_active=True,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    await _audit(db, user.id, "REGISTER", ip, ua, {"role": req.role})
    await db.commit()
    await db.refresh(user)
    return user


async def _issue_tokens(db: AsyncSession, user: IamUser) -> tuple[str, str, int]:
    access, expires_in = create_access_token(str(user.id), user.role, user.email)
    raw_refresh = generate_refresh_token()
    db.add(
        IamRefreshToken(
            user_id=user.id,
            token_hash=sha256(raw_refresh),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.iam_refresh_token_days),
        )
    )
    return access, raw_refresh, expires_in


async def login(db: AsyncSession, req: LoginRequest, ip, ua):
    res = await db.execute(select(IamUser).where(IamUser.email == req.email.lower()))
    user = res.scalar_one_or_none()
    if user is None or not verify_password(req.password, user.hashed_password) or not user.is_active:
        await _audit(db, user.id if user else None, "LOGIN_FAILED", ip, ua, {"email": req.email})
        await db.commit()
        if _WATCHMAN and ip:
            n = login_tracker().record_failure(ip)
            await on_failed_login(ip, n)
        raise INVALID_CREDENTIALS
    access, raw_refresh, expires_in = await _issue_tokens(db, user)
    await _audit(db, user.id, "LOGIN", ip, ua)
    await db.commit()
    return user, access, raw_refresh, expires_in


async def refresh_tokens(db: AsyncSession, raw: str, ip, ua):
    h = sha256(raw)
    res = await db.execute(select(IamRefreshToken).where(IamRefreshToken.token_hash == h))
    tok = res.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if tok is None or tok.expires_at.replace(tzinfo=timezone.utc) < now:
        raise INVALID_CREDENTIALS
    if tok.revoked:
        all_res = await db.execute(
            select(IamRefreshToken).where(IamRefreshToken.user_id == tok.user_id)
        )
        for t in all_res.scalars().all():
            t.revoked = True
        await _audit(db, tok.user_id, "TOKEN_REVOKED", ip, ua, {"reason": "reuse_detected"})
        await db.commit()
        raise INVALID_CREDENTIALS
    tok.revoked = True
    user = (await db.execute(select(IamUser).where(IamUser.id == tok.user_id))).scalar_one()
    access, raw_refresh, expires_in = await _issue_tokens(db, user)
    await _audit(db, user.id, "TOKEN_REFRESH", ip, ua)
    await db.commit()
    return access, raw_refresh, expires_in


async def logout(db: AsyncSession, raw: str, user_id: uuid.UUID, ip, ua) -> None:
    res = await db.execute(select(IamRefreshToken).where(IamRefreshToken.token_hash == sha256(raw)))
    tok = res.scalar_one_or_none()
    if tok and tok.user_id == user_id:
        tok.revoked = True
    await _audit(db, user_id, "LOGOUT", ip, ua)
    await db.commit()
