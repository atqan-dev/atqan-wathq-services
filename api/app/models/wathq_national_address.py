"""
National Address models for Wathq schema.
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, JSON
from sqlalchemy.sql import func

from app.db.base_class import Base


class Address(Base):
    """National Addresses table"""
    __tablename__ = "addresses"
    __table_args__ = {'schema': 'wathq'}
    
    pk_address_id = Column(String(50), primary_key=True, index=True)
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
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    request_body = Column(JSON, nullable=True)
