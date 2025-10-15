"""
Pydantic schemas for WATHQ offline data.
"""

from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel


class WathqOfflineDataBase(BaseModel):
    service_id: UUID
    tenant_id: int
    fetched_by: int
    full_external_url: str
    response_body: Dict[str, Any]


class WathqOfflineDataCreate(WathqOfflineDataBase):
    pass


class WathqOfflineDataUpdate(BaseModel):
    pass


class WathqOfflineDataInDBBase(WathqOfflineDataBase):
    id: UUID
    fetched_at: datetime

    class Config:
        from_attributes = True


class WathqOfflineData(WathqOfflineDataInDBBase):
    pass


class WathqOfflineDataInDB(WathqOfflineDataInDBBase):
    pass