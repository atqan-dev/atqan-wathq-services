"""
Pydantic schemas for management user operations.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr


class ManagementUserBase(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    name_ar: str | None = None  # Arabic name
    logo: str | None = None  # User avatar/logo URL/path
    is_active: bool | None = True
    is_super_admin: bool | None = False


class ManagementUserCreate(ManagementUserBase):
    email: EmailStr
    first_name: str
    last_name: str
    name_ar: str | None = None
    logo: str | None = None
    password: str


class ManagementUserUpdate(ManagementUserBase):
    password: str | None = None


class ManagementUserInDBBase(ManagementUserBase):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ManagementUser(ManagementUserInDBBase):
    pass


class ManagementUserInDB(ManagementUserInDBBase):
    hashed_password: str