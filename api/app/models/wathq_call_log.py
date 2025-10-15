"""
WATHQ API call logging model.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class WathqCallLog(Base):
    """
    Model to track all WATHQ external API calls.
    """

    __tablename__ = "wathq_call_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_slug = Column(String, nullable=False, index=True)  # e.g., 'commercial-registration'
    endpoint = Column(String, nullable=False)  # WATHQ endpoint called
    method = Column(String, nullable=False, default="POST")  # HTTP method
    status_code = Column(Integer, nullable=False)  # HTTP response status
    request_data = Column(JSON, nullable=True)  # Request payload
    response_body = Column(JSON, nullable=False)  # Response data
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    duration_ms = Column(Integer, nullable=True)  # Request duration in milliseconds

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")