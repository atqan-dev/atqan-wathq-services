"""
Pydantic schemas for Wathq Company Contract API responses.
"""

from typing import List, Optional
from pydantic import BaseModel


class Identity(BaseModel):
    id: str
    typeId: int
    typeName: str


class Nationality(BaseModel):
    id: int
    name: str


class EntityType(BaseModel):
    id: int
    name: str
    formId: int
    formName: str
    characters: List[dict]


class Stock(BaseModel):
    typeId: int
    typeName: str
    count: int
    value: float
    classReferenceID: Optional[int] = None
    className: Optional[str] = None


class StockCapital(BaseModel):
    typeId: int
    typeName: str
    cashCapital: float
    inKindCapital: float
    capital: float
    announcedCapital: float
    paidCapital: float
    stocks: List[Stock]


class ContributionCapital(BaseModel):
    typeId: int
    typeName: str
    cashCapital: float
    inKindCapital: float
    contributionValue: float
    totalCashContribution: int
    totalInKindContribution: int


class Capital(BaseModel):
    currencyId: int
    currencyName: str
    contributionCapital: Optional[ContributionCapital] = None
    stockCapital: Optional[StockCapital] = None


class FiscalYear(BaseModel):
    isFirst: bool
    calendarTypeId: int
    calendarTypeName: str
    endMonth: int
    endDay: int
    endYear: Optional[int] = None


class Guardian(BaseModel):
    name: str
    identity: Identity
    nationality: Nationality
    isFatherGuardian: bool


class PartnerShare(BaseModel):
    cashContributionCount: int
    inKindContributionCount: int
    totalContributionCount: int


class PartnerProfitLossDistribution(BaseModel):
    profitDistribution: int
    lossDistribution: int


class Party(BaseModel):
    name: str
    typeId: int
    typeName: str
    identity: Identity
    partnership: List[dict]
    partnerShare: Optional[PartnerShare] = None
    partnerProfitLossDistribution: Optional[PartnerProfitLossDistribution] = None
    nationality: Optional[Nationality] = None
    crNumber: Optional[str] = None
    licenseNo: Optional[str] = None
    guardian: Optional[Guardian] = None


class Position(BaseModel):
    id: int
    name: str


class Manager(BaseModel):
    name: str
    typeId: int
    typeName: str
    isLicensed: bool
    identity: Identity
    nationality: Nationality
    positions: List[Position]


class Permission(BaseModel):
    id: str
    name: str
    canIssuePOA: bool
    canDelegate: bool
    specialConditionText: Optional[str] = None
    exerciseMethodId: int
    exerciseMethodDescription: str


class ManagerWithPermissions(Manager):
    permissions: List[Permission]


class ManagementBoard(BaseModel):
    meetingQuorumId: int
    meetingQuorumName: str
    canDelegateAttendance: bool
    termYears: int
    wayOfWork: str
    meetingPlace: str
    additionalText: str
    positions: List[Position]


class Reward(BaseModel):
    id: str
    name: str


class DirectorsBoard(BaseModel):
    memberCount: int
    termYears: int
    value: int
    valueMax: int
    wayOfWork: str
    meetingPlace: str
    meetingQuorum: int
    meetingLegalQuorum: int
    canDelegateAttendance: bool
    boardCallMechanism: str
    membershipExpiryTerms: str
    additionalText: str
    rewards: List[Reward]
    positions: List[Position]


class Management(BaseModel):
    structureId: int
    structureName: str
    dismissalMethod: Optional[str] = None
    managers: List[Manager]
    managementBoard: Optional[ManagementBoard] = None
    directorsBoard: Optional[DirectorsBoard] = None


class Activity(BaseModel):
    id: str
    name: str


class Entity(BaseModel):
    crNationalNumber: str
    crNumber: Optional[int] = None
    name: str
    nameLangId: int
    nameLangDesc: str
    companyDuration: Optional[int] = None
    headquarterCityId: int
    headquarterCityName: str
    isLicenseBased: bool
    licenseIssuerNationalNo: Optional[str] = None
    licenseIssuerName: Optional[str] = None
    entityType: EntityType
    capital: Capital
    fiscalYear: Optional[FiscalYear] = None
    parties: List[Party]
    management: Management
    activities: List[Activity]


class NotificationChannel(BaseModel):
    id: int
    name: str


class PartnerDecision(BaseModel):
    id: int
    name: str
    approvePercentage: str
    approveAdditionalText: Optional[str] = None


class ProfitAllocation(BaseModel):
    percentage: int
    purpose: str


class SetAsideDetails(BaseModel):
    isSetAsideEnabled: bool
    profitAllocation: Optional[ProfitAllocation] = None


class Article(BaseModel):
    id: int
    text: str
    partId: Optional[int] = None
    partName: Optional[str] = None


class AdditionalArticle(BaseModel):
    title: str
    text: str
    partId: int
    partName: str


class CompanyContractInfo(BaseModel):
    contractCopyNumber: int
    contractDate: str
    entity: Entity
    notificationChannel: List[NotificationChannel]
    partnerDecision: List[PartnerDecision]
    additionalDecisionText: Optional[str] = None
    setAsideDetails: Optional[SetAsideDetails] = None
    articles: List[Article]
    additionalArticles: Optional[List[AdditionalArticle]] = None


class ManagementResponse(Management):
    pass


# ManagerResponse is just a list of ManagerWithPermissions
ManagerResponse = List[ManagerWithPermissions]


class Lookup(BaseModel):
    id: int
    nameAr: str
    nameEn: str


class ErrorResponse(BaseModel):
    code: str
    message: str