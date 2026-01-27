"""
Pydantic schemas for user operations.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    name_ar: str | None = None  # Arabic name
    logo: str | None = None  # User avatar/logo URL/path
    is_active: bool | None = True
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    first_name: str
    last_name: str
    name_ar: str | None = None
    logo: str | None = None
    password: str


# Properties to receive via API on creation with roles
class UserCreateWithRoles(UserCreate):
    role_ids: list[int] | None = []


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None


# Properties to receive via API on update with roles
class UserUpdateWithRoles(UserUpdate):
    role_ids: list[int] | None = None


class UserInDBBase(UserBase):
    id: int | None = None
    tenant_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# User with roles information
class UserWithRoles(UserInDBBase):
    roles: list["RoleSimple"] = []


# Simplified role for user response
class RoleSimple(BaseModel):
    id: int
    name: str
    description: str | None = None
    
    class Config:
        from_attributes = True


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


# Token payload schema
class TokenPayload(BaseModel):
    sub: int | None = None
    tenant_id: int | None = None
    tenant_slug: str | None = None
    is_management_user: bool = False
    is_super_admin: bool = False


# Import at the end to avoid circular imports
from app.schemas.permission import Role  # noqa: E402

UserWithRoles.model_rebuild()
