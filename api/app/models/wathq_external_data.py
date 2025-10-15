"""
WATHQ External Data model for caching external API responses.
"""

import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class WathqExternalData(Base):
    """
    Model to store WATHQ external API data with caching.
    This table acts as a cache for external WATHQ service calls.
    """

    __tablename__ = "wathq_external_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Tenant can be null for management-level data
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    
    # User who requested the data
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Service that was called
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True)
    
    # Request parameters used (for cache key generation)
    request_params = Column(JSON, nullable=True)
    
    # Cache key for quick lookup
    cache_key = Column(Text, nullable=False, index=True, unique=True)
    
    # The actual data from WATHQ API
    data = Column(JSON, nullable=False)
    
    # Response status from external API
    status_code = Column(Integer, nullable=True)
    
    # TTL for cache invalidation (in seconds)
    ttl_seconds = Column(Integer, default=3600)  # Default 1 hour
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relationships
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    user = relationship("User", foreign_keys=[user_id])
    service = relationship("Service", foreign_keys=[service_id])
