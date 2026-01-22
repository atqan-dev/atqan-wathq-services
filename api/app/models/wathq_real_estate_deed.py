"""
Real Estate Deed models for Wathq schema.
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Deed(Base):
    """Deeds master table"""
    __tablename__ = "deeds"
    __table_args__ = {'schema': 'wathq'}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deed_number = Column(String(50), nullable=True, index=True)
    deed_serial = Column(String(50), nullable=True, index=True)
    deed_date = Column(String(20), nullable=True)
    deed_text = Column(Text, nullable=True)
    deed_source = Column(String(255), nullable=True)
    deed_city = Column(String(100), nullable=True)
    deed_status = Column(String(50), nullable=True)
    deed_area = Column(Numeric(10, 2), nullable=True)
    deed_area_text = Column(Text, nullable=True)
    is_real_estate_constrained = Column(Boolean, nullable=True)
    is_real_estate_halted = Column(Boolean, nullable=True)
    is_real_estate_mortgaged = Column(Boolean, nullable=True)
    is_real_estate_testamented = Column(Boolean, nullable=True)
    
    # North limit
    limit_north_name = Column(String(100), nullable=True)
    limit_north_description = Column(Text, nullable=True)
    limit_north_length = Column(Numeric(10, 2), nullable=True)
    limit_north_length_char = Column(Text, nullable=True)
    
    # South limit
    limit_south_name = Column(String(100), nullable=True)
    limit_south_description = Column(Text, nullable=True)
    limit_south_length = Column(Numeric(10, 2), nullable=True)
    limit_south_length_char = Column(Text, nullable=True)
    
    # East limit
    limit_east_name = Column(String(100), nullable=True)
    limit_east_description = Column(Text, nullable=True)
    limit_east_length = Column(Numeric(10, 2), nullable=True)
    limit_east_length_char = Column(Text, nullable=True)
    
    # West limit
    limit_west_name = Column(String(100), nullable=True)
    limit_west_description = Column(Text, nullable=True)
    limit_west_length = Column(Numeric(10, 2), nullable=True)
    limit_west_length_char = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    request_body = Column(JSON, nullable=True)
    
    # Relationships
    owners = relationship("DeedOwner", back_populates="deed", cascade="all, delete-orphan")
    real_estates = relationship("DeedRealEstate", back_populates="deed", cascade="all, delete-orphan")


class DeedOwner(Base):
    """Deed Owners table"""
    __tablename__ = "deed_owners"
    __table_args__ = {'schema': 'wathq'}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deed_id = Column(Integer, ForeignKey('wathq.deeds.id', ondelete='CASCADE'), nullable=False)
    owner_name = Column(String(255), nullable=True)
    birth_date = Column(String(20), nullable=True)
    id_number = Column(String(50), nullable=True)
    id_type = Column(String(10), nullable=True)
    id_type_text = Column(String(50), nullable=True)
    owner_type = Column(String(50), nullable=True)
    nationality = Column(String(100), nullable=True)
    owning_area = Column(Numeric(10, 3), nullable=True)
    owning_amount = Column(Numeric(10, 2), nullable=True)
    constrained = Column(Integer, nullable=True)
    halt = Column(Integer, nullable=True)
    pawned = Column(Integer, nullable=True)
    testament = Column(Integer, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationship
    deed = relationship("Deed", back_populates="owners")


class DeedRealEstate(Base):
    """Deed Real Estates table"""
    __tablename__ = "deed_real_estates"
    __table_args__ = {'schema': 'wathq'}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deed_id = Column(Integer, ForeignKey('wathq.deeds.id', ondelete='CASCADE'), nullable=False)
    deed_serial = Column(String(50), nullable=True)
    region_code = Column(String(10), nullable=True)
    region_name = Column(String(100), nullable=True)
    city_code = Column(Integer, nullable=True)
    city_name = Column(String(100), nullable=True)
    real_estate_type_name = Column(String(100), nullable=True)
    land_number = Column(String(50), nullable=True)
    plan_number = Column(String(100), nullable=True)
    area = Column(Numeric(10, 2), nullable=True)
    area_text = Column(Text, nullable=True)
    district_code = Column(Integer, nullable=True)
    district_name = Column(String(100), nullable=True)
    location_description = Column(Text, nullable=True)
    constrained = Column(Integer, nullable=True)
    halt = Column(Integer, nullable=True)
    pawned = Column(Integer, nullable=True)
    testament = Column(Integer, nullable=True)
    is_north_riyadh_exceptioned = Column(Integer, nullable=True)
    
    # Border descriptions
    border_north_description = Column(Text, nullable=True)
    border_north_length = Column(Numeric(10, 2), nullable=True)
    border_north_length_char = Column(Text, nullable=True)
    border_south_description = Column(Text, nullable=True)
    border_south_length = Column(Numeric(10, 2), nullable=True)
    border_south_length_char = Column(Text, nullable=True)
    border_east_description = Column(Text, nullable=True)
    border_east_length = Column(String(50), nullable=True)  # VARCHAR due to mixed input like '22ز6'
    border_east_length_char = Column(Text, nullable=True)
    border_west_description = Column(Text, nullable=True)
    border_west_length = Column(Numeric(10, 2), nullable=True)
    border_west_length_char = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationship
    deed = relationship("Deed", back_populates="real_estates")
