"""
Pydantic schemas for Wathq SPL National Address API.
"""

from typing import List, Optional
from pydantic import BaseModel, RootModel


class NationalAddressInfo(BaseModel):
    title: Optional[str] = None
    address: Optional[str] = None
    address2: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    buildingNumber: Optional[str] = None
    street: Optional[str] = None
    district: Optional[str] = None
    districtId: Optional[str] = None
    city: Optional[str] = None
    cityId: Optional[str] = None
    postCode: Optional[str] = None
    additionalNumber: Optional[str] = None
    regionName: Optional[str] = None
    regionId: Optional[str] = None
    isPrimaryAddress: Optional[str] = None
    unitNumber: Optional[str] = None
    restriction: Optional[str] = None
    pkAddressId: Optional[str] = None
    status: Optional[str] = None


class NationalAddressResponse(RootModel[List[NationalAddressInfo]]):
    root: List[NationalAddressInfo]