"""
Real Estate Deed schemas for Wathq.
"""

from typing import List, Optional, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


# DeedOwner Schemas
class DeedOwnerBase(BaseModel):
    owner_name: Optional[str] = None
    birth_date: Optional[str] = None
    id_number: Optional[str] = None
    id_type: Optional[str] = None
    id_type_text: Optional[str] = None
    owner_type: Optional[str] = None
    nationality: Optional[str] = None
    owning_area: Optional[Decimal] = None
    owning_amount: Optional[Decimal] = None
    constrained: Optional[int] = None
    halt: Optional[int] = None
    pawned: Optional[int] = None
    testament: Optional[int] = None


class DeedOwnerCreate(DeedOwnerBase):
    deed_id: int


class DeedOwnerUpdate(DeedOwnerBase):
    pass


class DeedOwner(DeedOwnerBase):
    id: int
    deed_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# DeedRealEstate Schemas
class DeedRealEstateBase(BaseModel):
    deed_serial: Optional[str] = None
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    city_code: Optional[int] = None
    city_name: Optional[str] = None
    real_estate_type_name: Optional[str] = None
    land_number: Optional[str] = None
    plan_number: Optional[str] = None
    area: Optional[Decimal] = None
    area_text: Optional[str] = None
    district_code: Optional[int] = None
    district_name: Optional[str] = None
    location_description: Optional[str] = None
    constrained: Optional[int] = None
    halt: Optional[int] = None
    pawned: Optional[int] = None
    testament: Optional[int] = None
    is_north_riyadh_exceptioned: Optional[int] = None
    border_north_description: Optional[str] = None
    border_north_length: Optional[Decimal] = None
    border_north_length_char: Optional[str] = None
    border_south_description: Optional[str] = None
    border_south_length: Optional[Decimal] = None
    border_south_length_char: Optional[str] = None
    border_east_description: Optional[str] = None
    border_east_length: Optional[str] = None
    border_east_length_char: Optional[str] = None
    border_west_description: Optional[str] = None
    border_west_length: Optional[Decimal] = None
    border_west_length_char: Optional[str] = None


class DeedRealEstateCreate(DeedRealEstateBase):
    deed_id: int


class DeedRealEstateUpdate(DeedRealEstateBase):
    pass


class DeedRealEstate(DeedRealEstateBase):
    id: int
    deed_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# Deed Schemas
class DeedBase(BaseModel):
    deed_number: Optional[str] = None
    deed_serial: Optional[str] = None
    deed_date: Optional[str] = None
    deed_text: Optional[str] = None
    deed_source: Optional[str] = None
    deed_city: Optional[str] = None
    deed_status: Optional[str] = None
    deed_area: Optional[Decimal] = None
    deed_area_text: Optional[str] = None
    is_real_estate_constrained: Optional[bool] = None
    is_real_estate_halted: Optional[bool] = None
    is_real_estate_mortgaged: Optional[bool] = None
    is_real_estate_testamented: Optional[bool] = None
    limit_north_name: Optional[str] = None
    limit_north_description: Optional[str] = None
    limit_north_length: Optional[Decimal] = None
    limit_north_length_char: Optional[str] = None
    limit_south_name: Optional[str] = None
    limit_south_description: Optional[str] = None
    limit_south_length: Optional[Decimal] = None
    limit_south_length_char: Optional[str] = None
    limit_east_name: Optional[str] = None
    limit_east_description: Optional[str] = None
    limit_east_length: Optional[Decimal] = None
    limit_east_length_char: Optional[str] = None
    limit_west_name: Optional[str] = None
    limit_west_description: Optional[str] = None
    limit_west_length: Optional[Decimal] = None
    limit_west_length_char: Optional[str] = None


class DeedCreate(DeedBase):
    pass


class DeedUpdate(DeedBase):
    pass


class Deed(DeedBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    request_body: Optional[Any] = None
    
    # Nested relationships
    owners: List[DeedOwner] = []
    real_estates: List[DeedRealEstate] = []

    model_config = ConfigDict(from_attributes=True)
