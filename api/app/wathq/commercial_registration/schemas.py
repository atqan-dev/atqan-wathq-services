"""
Pydantic schemas for Wathq Commercial Registration API responses.
"""

from typing import List, Optional, Union
from pydantic import BaseModel


class EntityType(BaseModel):
    id: int
    name: str
    formId: Optional[int] = None
    formName: Optional[str] = None
    characters: Optional[List[dict]] = None


class Status(BaseModel):
    id: int
    name: str


class Activity(BaseModel):
    id: str
    name: str


class Identity(BaseModel):
    id: str
    typeId: int
    typeName: str


class Manager(BaseModel):
    name: str
    typeId: int
    typeName: str
    isLicensed: bool
    identity: Identity
    nationality: dict
    positions: List[dict]


class Owner(BaseModel):
    name: str
    typeId: int
    typeName: str
    identity: Identity
    partnership: List[dict]
    partnerShare: Optional[dict] = None
    nationality: Optional[dict] = None
    licenseNo: Optional[str] = None
    crNumber: Optional[str] = None


class Capital(BaseModel):
    currencyId: Optional[int] = None
    currencyName: Optional[str] = None
    capital: Optional[float] = None
    contributionCapital: Optional[dict] = None
    stockCapital: Optional[dict] = None


class Branch(BaseModel):
    crNationalNumber: str
    crNumber: str
    versionNo: int
    name: str
    isMain: bool
    mainCrNationalNumber: Optional[str] = None
    mainCrNumber: Optional[str] = None
    entityType: dict


class RelatedCR(BaseModel):
    crNationalNumber: str
    name: str
    isMain: bool
    status: Status
    relation: dict
    positions: List[dict]
    parties: List[dict]


class Related(BaseModel):
    result: dict
    name: str
    identity: Identity
    related: List[RelatedCR]


class FullInfo(BaseModel):
    crNationalNumber: str
    crNumber: str
    versionNo: int
    name: str
    nameLangId: Optional[int] = None
    nameLangDesc: Optional[str] = None
    crCapital: Optional[float] = None
    companyDuration: Optional[int] = None
    isMain: bool
    issueDateGregorian: str
    issueDateHijri: str
    mainCrNationalNumber: Optional[str] = None
    mainCrNumber: Optional[str] = None
    inLiquidationProcess: bool
    hasEcommerce: bool
    headquarterCityId: int
    headquarterCityName: str
    isLicenseBased: bool
    licenseIssuerNationalNumber: Optional[str] = None
    licenseIssuerName: Optional[str] = None
    partnersNationalityId: Optional[int] = None
    PartnersNationalityName: Optional[str] = None
    entityType: EntityType
    status: dict
    contactInfo: Optional[dict] = None
    eCommerce: Optional[dict] = None
    capital: Optional[Capital] = None
    fiscalYear: Optional[dict] = None
    parties: Optional[List[Owner]] = None
    management: Optional[dict] = None
    activities: List[Activity]


class BasicInfo(BaseModel):
    crNationalNumber: str
    crNumber: str
    versionNo: int
    name: str
    duration: Optional[int] = None
    isMain: bool
    issueDateGregorian: str
    issueDateHijri: str
    mainCrNationalNumber: Optional[str] = None
    mainCrNumber: Optional[str] = None
    inLiquidationProcess: bool
    hasEcommerce: bool
    headquarterCityId: int
    headquarterCityName: str
    isLicenseBased: bool
    entityType: EntityType
    status: Status
    activities: List[Activity]


class CRNationalNumber(BaseModel):
    crNationalNumber: str


class Owns(BaseModel):
    ownsCr: bool


class Lookup(BaseModel):
    id: int
    nameAr: str
    nameEn: str


class ErrorResponse(BaseModel):
    code: str
    message: str