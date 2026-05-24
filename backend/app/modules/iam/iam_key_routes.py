import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.iam import iam_key_service as keys
from app.modules.iam.iam_models import IamUser
from app.modules.iam.iam_schemas import ApiKeyCreateRequest, ApiKeyResponse

router = APIRouter()


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    req: ApiKeyCreateRequest,
    user: IamUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    api_key, raw = await keys.create_api_key(db, user, req)
    resp = ApiKeyResponse.model_validate(api_key)
    resp.raw_key = raw
    return resp


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def list_api_keys(
    user: IamUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await keys.list_api_keys(db, user.id)


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    user: IamUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await keys.revoke_api_key(db, uuid.UUID(key_id), user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
