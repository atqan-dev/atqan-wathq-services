"""
Pydantic schemas for API Request Counter.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class ApiRequestCounterBase(BaseModel):
    """Base schema for API request counter."""
    request_type: str = Field(..., description="Type: internal/external/cached")
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    response_status: int = Field(..., description="HTTP status code")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    is_successful: bool = Field(True, description="Whether request was successful")
    is_cached: bool = Field(False, description="Whether response was from cache")


class ApiRequestCounterCreate(ApiRequestCounterBase):
    """Schema for creating API request counter entry."""
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    management_user_id: Optional[int] = None
    service_id: Optional[UUID] = None
    service_slug: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_params: Optional[Dict[str, Any]] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    error_message: Optional[str] = None
    is_rate_limited: bool = False


class ApiRequestCounter(ApiRequestCounterBase):
    """Schema for API request counter response."""
    id: UUID
    user_id: Optional[int]
    tenant_id: Optional[int]
    management_user_id: Optional[int]
    service_id: Optional[UUID]
    service_slug: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ApiRequestStats(BaseModel):
    """Schema for API request statistics."""
    period: str = Field(..., description="Time period for stats")
    total_requests: int
    successful_requests: int
    failed_requests: int
    cached_requests: int
    external_requests: int
    internal_requests: int
    avg_response_time_ms: float
    max_response_time_ms: int
    min_response_time_ms: int
    cache_hit_rate: float
    success_rate: float
    unique_users: int
    unique_endpoints: int


class EndpointStats(BaseModel):
    """Schema for endpoint-specific statistics."""
    endpoint: str
    method: str
    total_calls: int
    success_rate: float
    avg_response_time_ms: float
    cached_calls: int
    failed_calls: int
    last_called: datetime


class UserRequestStats(BaseModel):
    """Schema for user-specific request statistics."""
    user_id: int
    user_email: str
    tenant_name: Optional[str]
    total_requests: int
    successful_requests: int
    failed_requests: int
    external_calls: int
    internal_calls: int
    cached_calls: int
    avg_response_time_ms: float
    most_used_endpoints: List[Dict[str, Any]]
    last_request: datetime


class ServiceUsageStats(BaseModel):
    """Schema for WATHQ service usage statistics."""
    service_id: UUID
    service_name: str
    service_slug: str
    total_calls: int
    cached_calls: int
    direct_calls: int
    success_rate: float
    avg_response_time_ms: float
    unique_users: int
    total_cost: Optional[float] = Field(None, description="Estimated cost if applicable")


class RequestTimeline(BaseModel):
    """Schema for request timeline data."""
    timestamp: datetime
    request_count: int
    success_count: int
    failed_count: int
    avg_response_time_ms: float
    external_count: int
    internal_count: int
    cached_count: int


class RequestDetails(BaseModel):
    """Detailed request information for management view."""
    id: UUID
    request_type: str
    endpoint: str
    method: str
    user_email: Optional[str]
    tenant_name: Optional[str]
    service_name: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_params: Optional[Dict[str, Any]]
    response_status: int
    response_time_ms: int
    response_size: Optional[int]
    error_message: Optional[str]
    is_successful: bool
    is_cached: bool
    is_rate_limited: bool
    created_at: datetime


class DashboardStats(BaseModel):
    """Schema for management dashboard statistics."""
    # Overview
    total_requests_today: int
    total_requests_this_week: int
    total_requests_this_month: int
    
    # Performance
    avg_response_time_today_ms: float
    avg_response_time_trend: str  # up/down/stable
    
    # Success metrics
    success_rate_today: float
    success_rate_this_week: float
    
    # Cache metrics
    cache_hit_rate_today: float
    cache_hit_rate_this_week: float
    
    # Top metrics
    top_endpoints: List[EndpointStats]
    top_users: List[UserRequestStats]
    top_services: List[ServiceUsageStats]
    
    # Timeline (last 24 hours)
    hourly_timeline: List[RequestTimeline]
    
    # Alerts
    slow_endpoints: List[Dict[str, Any]]
    failing_endpoints: List[Dict[str, Any]]
    rate_limited_users: List[Dict[str, Any]]
