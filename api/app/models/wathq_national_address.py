"""
National Address models for Wathq schema.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class Address(Base):
    """
    National Addresses table.
    Links to wathq_call_logs via log_id for data traceability.
    Same address data can be repeated but each record is linked to a unique call log.
    """

    __tablename__ = "addresses"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_id = Column(
        UUID(as_uuid=True), ForeignKey("wathq_call_logs.id"), nullable=True, index=True
    )
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    pk_address_id = Column(String(50), nullable=True, index=True)
    title = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    address2 = Column(Text, nullable=True)
    latitude = Column(Numeric(11, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    building_number = Column(String(50), nullable=True)
    street = Column(String(255), nullable=True)
    district = Column(String(255), nullable=True)
    district_id = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    city_id = Column(String(50), nullable=True)
    post_code = Column(String(20), nullable=True, index=True)
    additional_number = Column(String(50), nullable=True)
    region_name = Column(String(100), nullable=True)
    region_id = Column(String(50), nullable=True, index=True)
    is_primary_address = Column(Boolean, nullable=True, index=True)
    unit_number = Column(String(50), nullable=True)
    restriction = Column(Text, nullable=True)
    status = Column(String(50), nullable=True)

    # Audit fields
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    request_body = Column(JSON, nullable=True)
