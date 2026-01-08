"""
National Address schemas for Wathq.
"""

from typing import Optional, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class AddressBase(BaseModel):
    title: Optional[str] = None
    address: Optional[str] = None
    address2: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    building_number: Optional[str] = None
    street: Optional[str] = None
    district: Optional[str] = None
    district_id: Optional[str] = None
    city: Optional[str] = None
    city_id: Optional[str] = None
    post_code: Optional[str] = None
    additional_number: Optional[str] = None
    region_name: Optional[str] = None
    region_id: Optional[str] = None
    is_primary_address: Optional[bool] = None
    unit_number: Optional[str] = None
    restriction: Optional[str] = None
    status: Optional[str] = None


class AddressCreate(AddressBase):
    pk_address_id: str


class AddressUpdate(AddressBase):
    pass


class Address(AddressBase):
    pk_address_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    request_body: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)
