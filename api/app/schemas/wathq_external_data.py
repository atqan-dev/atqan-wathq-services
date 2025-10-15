"""
Pydantic schemas for WATHQ External Data.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class WathqExternalDataBase(BaseModel):
    """Base schema for WATHQ external data."""
    tenant_id: Optional[int] = Field(None, description="Tenant ID (null for management data)")
    service_id: UUID = Field(..., description="Service ID that was called")
    request_params: Optional[Dict[str, Any]] = Field(None, description="Request parameters")
    data: Dict[str, Any] = Field(..., description="Response data from WATHQ API")
    ttl_seconds: int = Field(3600, description="Cache TTL in seconds")


class WathqExternalDataCreate(WathqExternalDataBase):
    """Schema for creating WATHQ external data entry."""
    pass


class WathqExternalDataUpdate(BaseModel):
    """Schema for updating WATHQ external data."""
    data: Optional[Dict[str, Any]] = None
    ttl_seconds: Optional[int] = None


class WathqExternalDataInDBBase(WathqExternalDataBase):
    """Base schema for WATHQ external data in database."""
    id: UUID
    user_id: int
    cache_key: str
    status_code: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    expires_at: datetime

    class Config:
        from_attributes = True


class WathqExternalData(WathqExternalDataInDBBase):
    """Schema for WATHQ external data response."""
    pass


class WathqExternalDataInDB(WathqExternalDataInDBBase):
    """Schema for WATHQ external data in database with all fields."""
    pass


class WathqServiceRequest(BaseModel):
    """Schema for requesting data from a WATHQ service."""
    service_slug: str = Field(..., description="Service slug to call")
    params: Optional[Dict[str, Any]] = Field(None, description="Service-specific parameters")
    force_refresh: bool = Field(False, description="Force refresh from external API")


class WathqServiceResponse(BaseModel):
    """Schema for WATHQ service response."""
    service: str
    data: Dict[str, Any]
    cached: bool = Field(..., description="Whether data was from cache or fresh")
    cache_expires_at: Optional[datetime] = None
    status: str = Field("success", description="Response status")
    message: Optional[str] = None


class WathqBulkServiceRequest(BaseModel):
    """Schema for bulk WATHQ service requests."""
    services: list[WathqServiceRequest] = Field(..., description="List of services to call")


class WathqBulkServiceResponse(BaseModel):
    """Schema for bulk WATHQ service responses."""
    results: list[WathqServiceResponse]
    total_requested: int
    successful: int
    failed: int
