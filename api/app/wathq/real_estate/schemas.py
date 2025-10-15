"""
Pydantic schemas for Wathq Real Estate API.
"""

from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class IdType(str, Enum):
    NATIONAL_ID = "National_ID"
    RESIDENT_ID = "Resident_ID"
    PASSPORT = "Passport"
    CR_NO = "CR_NO"
    ENDOWMENT_DEED_NO = "Endowment_Deed_No"
    LICENSE_NO = "license_No"
    FOREIGN_CR_NO = "Foreign_CR_No"
    GOV_NATIONAL_ID = "Gov_National_ID"


class DeedDetails(BaseModel):
    deedNumber: int
    deedSerial: int
    deedDate: Optional[str] = None
    deedText: Optional[str] = None


class CourtDetails(BaseModel):
    deedSource: Optional[str] = None
    deedCity: Optional[str] = None


class DeedInfo(BaseModel):
    deedArea: Optional[float] = None
    deedAreaText: Optional[str] = None
    isRealEstateConstrained: Optional[bool] = None
    isRealEstateHalted: Optional[bool] = None
    isRealEstateMortgaged: Optional[bool] = None
    isRealEstateTestamented: Optional[bool] = None


class OwnerDetail(BaseModel):
    ownerName: Optional[str] = None
    birthDate: Optional[str] = None
    idNumber: Optional[str] = None
    idType: str
    idTypeText: str
    ownerType: Optional[str] = None
    nationality: Optional[str] = None
    owningArea: float
    owningAmount: float
    constrained: int
    halt: int
    pawned: int
    testament: int


class DeedLimitsDetails(BaseModel):
    northLimitName: Optional[str] = None
    northLimitDescription: Optional[str] = None
    northLimitLength: float
    northLimitLengthChar: Optional[str] = None
    southLimitName: Optional[str] = None
    southLimitDescription: Optional[str] = None
    southLimitLength: float
    southLimitLengthChar: Optional[str] = None
    eastLimitName: Optional[str] = None
    eastLimitDescription: Optional[str] = None
    eastLimitLength: float
    eastLimitLengthChar: Optional[str] = None
    westLimitName: Optional[str] = None
    westLimitDescription: Optional[str] = None
    westLimitLength: float
    westLimitLengthChar: Optional[str] = None


class RealEstateBorderDetails(BaseModel):
    northLimitDescription: Optional[str] = None
    northLimitLength: float
    northLimitLengthChar: Optional[str] = None
    southLimitDescription: Optional[str] = None
    southLimitLength: float
    southLimitLengthChar: Optional[str] = None
    eastLimitDescription: Optional[str] = None
    eastLimitLength: float
    eastLimitLengthChar: Optional[str] = None
    westLimitDescription: Optional[str] = None
    westLimitLength: float
    westLimitLengthChar: Optional[str] = None


class RealEstateDetail(BaseModel):
    deedSerial: int
    regionCode: Optional[str] = None
    regionName: Optional[str] = None
    cityCode: int
    cityName: Optional[str] = None
    realEstateTypeName: Optional[str] = None
    landNumber: Optional[str] = None
    planNumber: Optional[str] = None
    area: float
    areaText: Optional[str] = None
    districtCode: Optional[int] = None
    districtName: Optional[str] = None
    locationDescription: Optional[str] = None
    constrained: int
    halt: int
    pawned: int
    testament: int
    isNorthRiyadhExceptioned: int
    realEstateBorderDetails: Optional[RealEstateBorderDetails] = None


class DeedResponse(BaseModel):
    deedDetails: DeedDetails
    courtDetails: Optional[CourtDetails] = None
    deedStatus: Optional[str] = None
    deedInfo: Optional[DeedInfo] = None
    ownerDetails: Optional[List[OwnerDetail]] = None
    deedLimitsDetails: Optional[DeedLimitsDetails] = None
    realEstateDetails: Optional[List[RealEstateDetail]] = None