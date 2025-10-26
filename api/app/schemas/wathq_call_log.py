"""
Pydantic schemas for WATHQ call logs.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class WathqCallLogBase(BaseModel):
    tenant_id: Optional[int] = None  # Nullable for management users
    user_id: Optional[int] = None  # Nullable for management users
    management_user_id: Optional[int] = None  # For management user calls
    service_slug: str
    endpoint: str
    method: str = "POST"
    status_code: int
    request_data: Optional[Dict[str, Any]] = None
    response_body: Dict[str, Any]
    duration_ms: Optional[int] = None


class WathqCallLogCreate(WathqCallLogBase):
    pass


class WathqCallLogUpdate(BaseModel):
    pass


class WathqCallLogInDBBase(WathqCallLogBase):
    id: UUID
    fetched_at: datetime

    class Config:
        from_attributes = True


class WathqCallLog(WathqCallLogInDBBase):
    pass


class WathqCallLogInDB(WathqCallLogInDBBase):
    pass


# Statistics schemas
class ServiceUsageStats(BaseModel):
    service_slug: str
    total_calls: int
    success_calls: int
    error_calls: int
    avg_duration_ms: Optional[float] = None


class TenantUsageStats(BaseModel):
    tenant_id: int
    total_calls: int
    services_used: int
    last_call_at: Optional[datetime] = None