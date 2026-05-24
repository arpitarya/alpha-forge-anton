import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.iam.iam_key_models import IamApiKey, IamAuditLog
from app.modules.iam.iam_models import IamUser
from app.modules.iam.iam_schemas import ApiKeyCreateRequest
from app.modules.iam.iam_utils import generate_api_key, sha256


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> IamUser | None:
    return (await db.execute(select(IamUser).where(IamUser.id == user_id))).scalar_one_or_none()


async def list_users(db: AsyncSession) -> list[IamUser]:
    return list((await db.execute(select(IamUser))).scalars().all())


async def create_api_key(
    db: AsyncSession, user: IamUser, req: ApiKeyCreateRequest
) -> tuple[IamApiKey, str]:
    if req.role == "owner" and user.role != "owner":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot grant role above your own")
    count = (
        await db.execute(
            select(func.count())
            .select_from(IamApiKey)
            .where(IamApiKey.user_id == user.id, IamApiKey.revoked.is_(False))
        )
    ).scalar_one()
    if count >= settings.iam_max_api_keys_per_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "API key limit reached")
    raw, key_hash, key_prefix = generate_api_key()
    expires_at = None
    if req.expires_days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=req.expires_days)
    api_key = IamApiKey(
        user_id=user.id,
        label=req.label,
        key_hash=key_hash,
        key_prefix=key_prefix,
        role=req.role,
        expires_at=expires_at,
    )
    db.add(api_key)
    db.add(IamAuditLog(user_id=user.id, event="API_KEY_CREATED", detail={"label": req.label}))
    await db.commit()
    await db.refresh(api_key)
    return api_key, raw


async def revoke_api_key(db: AsyncSession, api_key_id: uuid.UUID, user: IamUser) -> None:
    res = await db.execute(select(IamApiKey).where(IamApiKey.id == api_key_id))
    key = res.scalar_one_or_none()
    if key is None or (key.user_id != user.id and user.role != "owner"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "API key not found")
    key.revoked = True
    db.add(IamAuditLog(user_id=user.id, event="API_KEY_REVOKED", detail={"key_id": str(key.id)}))
    await db.commit()


async def list_api_keys(db: AsyncSession, user_id: uuid.UUID) -> list[IamApiKey]:
    res = await db.execute(select(IamApiKey).where(IamApiKey.user_id == user_id))
    return list(res.scalars().all())


async def authenticate_api_key(db: AsyncSession, raw: str) -> IamUser | None:
    res = await db.execute(select(IamApiKey).where(IamApiKey.key_hash == sha256(raw)))
    key = res.scalar_one_or_none()
    if key is None or key.revoked:
        return None
    if key.expires_at and key.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return None
    key.last_used_at = datetime.now(timezone.utc)
    user = await get_user_by_id(db, key.user_id)
    await db.commit()
    return user if user and user.is_active else None


async def list_audit(db: AsyncSession, limit: int = 200) -> list[IamAuditLog]:
    res = await db.execute(select(IamAuditLog).order_by(IamAuditLog.created_at.desc()).limit(limit))
    return list(res.scalars().all())
