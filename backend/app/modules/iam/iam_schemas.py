import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    full_name: str
    role: Literal["owner", "viewer"] = "viewer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ApiKeyCreateRequest(BaseModel):
    label: str
    role: Literal["owner", "viewer"] = "viewer"
    expires_days: int | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    key_prefix: str
    role: str
    expires_at: datetime | None
    created_at: datetime
    raw_key: str | None = None


class AuditEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    event: str
    ip_address: str | None
    user_agent: str | None
    detail: dict | None
    created_at: datetime
