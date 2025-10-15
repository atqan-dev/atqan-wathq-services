"""
API Request Counter model for tracking internal and external API calls.
"""

import uuid
from enum import Enum
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RequestType(str, Enum):
    """Type of API request."""
    INTERNAL = "internal"  # Internal API calls within the system
    EXTERNAL = "external"  # External WATHQ API calls
    CACHED = "cached"      # Served from cache


class ApiRequestCounter(Base):
    """
    Model to track and count API requests for analytics.
    """

    __tablename__ = "api_request_counters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Request identification
    request_type = Column(String, nullable=False, index=True)  # internal/external/cached
    endpoint = Column(String, nullable=False, index=True)  # API endpoint called
    method = Column(String, nullable=False)  # HTTP method (GET, POST, etc.)
    
    # User and tenant information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    management_user_id = Column(Integer, ForeignKey("management_users.id"), nullable=True, index=True)
    
    # Service information (for WATHQ calls)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=True, index=True)
    service_slug = Column(String, nullable=True, index=True)
    
    # Request details
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    request_params = Column(JSON, nullable=True)  # Query params or body (sanitized)
    request_size = Column(Integer, nullable=True)  # Request size in bytes
    
    # Response details
    response_status = Column(Integer, nullable=False)  # HTTP status code
    response_time_ms = Column(Integer, nullable=False)  # Response time in milliseconds
    response_size = Column(Integer, nullable=True)  # Response size in bytes
    error_message = Column(Text, nullable=True)  # Error message if failed
    
    # Flags
    is_successful = Column(Boolean, default=True)
    is_cached = Column(Boolean, default=False)
    is_rate_limited = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    management_user = relationship("ManagementUser", foreign_keys=[management_user_id])
    service = relationship("Service", foreign_keys=[service_id])


class ApiRequestSummary(Base):
    """
    Aggregated summary of API requests for reporting.
    Updated periodically for fast dashboard access.
    """

    __tablename__ = "api_request_summaries"

    id = Column(Integer, primary_key=True, index=True)
    
    # Summary period
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String, nullable=False)  # hourly, daily, weekly, monthly
    
    # Aggregated data
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    endpoint = Column(String, nullable=True, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=True, index=True)
    
    # Counters
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    cached_requests = Column(Integer, default=0)
    external_requests = Column(Integer, default=0)
    internal_requests = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time_ms = Column(Numeric(10, 2), nullable=True)
    max_response_time_ms = Column(Integer, nullable=True)
    min_response_time_ms = Column(Integer, nullable=True)
    total_response_size_bytes = Column(Integer, nullable=True)
    
    # Rate limiting
    rate_limited_requests = Column(Integer, default=0)
    
    # Unique users
    unique_users = Column(Integer, default=0)
    unique_ips = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    user = relationship("User", foreign_keys=[user_id])
    service = relationship("Service", foreign_keys=[service_id])
