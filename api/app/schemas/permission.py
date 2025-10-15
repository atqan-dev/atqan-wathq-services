"""
Pydantic schemas for permissions and roles.
"""

from datetime import datetime

from pydantic import BaseModel


# Permission schemas
class PermissionBase(BaseModel):
    name: str | None = None
    description: str | None = None
    resource: str | None = None
    action: str | None = None
    scope: str | None = "tenant"
    is_active: bool | None = True


class PermissionCreate(PermissionBase):
    name: str
    resource: str
    action: str
    description: str | None = None


class PermissionUpdate(PermissionBase):
    pass


class PermissionInDBBase(PermissionBase):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Permission(PermissionInDBBase):
    pass


class PermissionInDB(PermissionInDBBase):
    pass


# Role schemas
class RoleBase(BaseModel):
    name: str | None = None
    description: str | None = None
    tenant_id: int | None = None
    is_default: bool | None = False
    is_active: bool | None = True


class RoleCreate(RoleBase):
    name: str
    description: str | None = None
    permission_ids: list[int] | None = []


class RoleUpdate(RoleBase):
    permission_ids: list[int] | None = None


class RoleInDBBase(RoleBase):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Role(RoleInDBBase):
    permissions: list[Permission] = []


class RoleInDB(RoleInDBBase):
    pass


# User role assignment schemas
class UserRoleAssignment(BaseModel):
    user_id: int
    role_ids: list[int]
