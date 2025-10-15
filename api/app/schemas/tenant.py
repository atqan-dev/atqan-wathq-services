"""
Pydantic schemas for tenant operations.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# Shared properties
class TenantBase(BaseModel):
    name: str | None = None
    name_ar: str | None = None  # Arabic name
    slug: str | None = Field(
        None, pattern="^[a-z0-9-]+$"
    )  # Only lowercase, numbers, hyphens
    description: str | None = None
    logo: str | None = None  # Logo URL/path
    is_active: bool | None = True
    max_users: int | None = 100


# Properties to receive via API on creation
class TenantCreate(TenantBase):
    name: str
    name_ar: str | None = None
    slug: str = Field(..., pattern="^[a-z0-9-]+$", min_length=3, max_length=50)
    description: str | None = None
    logo: str | None = None


# Properties to receive via API on update
class TenantUpdate(TenantBase):
    pass


class TenantInDBBase(TenantBase):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class Tenant(TenantInDBBase):
    users_count: int | None = 0


# Additional properties stored in DB
class TenantInDB(TenantInDBBase):
    pass
