from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


class UserUpdateRequest(BaseModel):
    role: str | None = None
    is_active: bool | None = None


class PermissionsMatrixOut(BaseModel):
    roles: list[str]
    agent_types: list[str]
    matrix: dict[str, list[str]]


class PermissionToggleRequest(BaseModel):
    role: str
    agent_type: str
    allowed: bool


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    action: str
    user_id: int | None
    user_email: str | None
    role: str | None
    request_id: int | None
    subtask_id: int | None
    context: dict | None
    created_at: datetime
