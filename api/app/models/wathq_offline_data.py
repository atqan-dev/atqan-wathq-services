"""
WATHQ offline data storage model.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class WathqOfflineData(Base):
    """
    Model to store WATHQ API responses for offline access.
    """

    __tablename__ = "wathq_offline_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    fetched_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    full_external_url = Column(Text, nullable=False)
    response_body = Column(JSON, nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    service = relationship("Service")
    tenant = relationship("Tenant")
    user = relationship("User")