"""
Pydantic schemas for service operations with WATHQ integration.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import List

from pydantic import BaseModel


# Service schemas
class ServiceBase(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    category: str | None = "wathq"
    price: Decimal | None = None
    is_active: bool | None = True
    requires_approval: bool | None = True


class ServiceCreate(ServiceBase):
    name: str
    slug: str
    price: Decimal
    description: str | None = None
    category: str = "wathq"


class ServiceUpdate(ServiceBase):
    pass


class ServiceInDBBase(ServiceBase):
    id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Service(ServiceInDBBase):
    pass


class ServiceInDB(ServiceInDBBase):
    pass


# TenantService schemas
class TenantServiceBase(BaseModel):
    tenant_id: int | None = None
    service_id: UUID | None = None
    is_active: bool | None = True
    max_users: int | None = 10
    wathq_api_key: str | None = None


class TenantServiceCreate(TenantServiceBase):
    tenant_id: int
    service_id: UUID
    max_users: int = 10


class TenantServiceUpdate(TenantServiceBase):
    pass


class TenantServiceRequest(BaseModel):
    service_id: UUID
    max_users: int = 10
    wathq_api_key: str


class TenantServiceApproval(BaseModel):
    tenant_service_id: int
    approved: bool = True


class UserServiceAssignment(BaseModel):
    user_id: int
    service_id: UUID


class TenantServiceInDBBase(TenantServiceBase):
    id: int | None = None
    is_approved: bool | None = False
    usage_count: int | None = 0
    registered_at: datetime | None = None
    approved_at: datetime | None = None
    approved_by: int | None = None

    class Config:
        from_attributes = True


class TenantService(TenantServiceInDBBase):
    service: Service | None = None

    class Config:
        from_attributes = True


class TenantServiceInDB(TenantServiceInDBBase):
    pass


# Response schemas
class ServiceListResponse(BaseModel):
    services: List[Service]
    total: int


class TenantServiceListResponse(BaseModel):
    tenant_services: List[TenantService]
    total: int


class UserAuthorizedServicesResponse(BaseModel):
    services: List[Service]
    user_id: int


class ManagementServicesResponse(BaseModel):
    services: List[Service]
    total: int
