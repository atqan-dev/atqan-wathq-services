"""
Pydantic schemas for Wathq Company Contract API responses.

Based on Wathq OpenAPI Spec v2.0.0
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field


class Identity(BaseModel):
    id: Optional[str] = None
    typeId: Optional[int] = None
    typeName: Optional[str] = None


class Nationality(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Character(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class EntityType(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    formId: Optional[int] = None
    formName: Optional[str] = None
    characters: Optional[List[Character]] = None


class Stock(BaseModel):
    typeId: Optional[int] = None
    typeName: Optional[str] = None
    count: Optional[int] = None
    value: Optional[float] = None
    classReferenceID: Optional[str] = None
    className: Optional[str] = None


class StockCapital(BaseModel):
    typeId: Optional[int] = None
    typeName: Optional[str] = None
    cashCapital: Optional[float] = None
    inKindCapital: Optional[float] = None
    capital: Optional[float] = None
    announcedCapital: Optional[float] = None
    paidCapital: Optional[float] = None
    stocks: Optional[List[Stock]] = None


class ContributionCapital(BaseModel):
    typeId: Optional[int] = None
    typeName: Optional[str] = None
    cashCapital: Optional[float] = None
    inKindCapital: Optional[float] = None
    contributionValue: Optional[float] = None
    totalCashContribution: Optional[int] = None
    totalInKindContribution: Optional[int] = None


class Capital(BaseModel):
    currencyId: Optional[int] = None
    currencyName: Optional[str] = None
    contributionCapital: Optional[ContributionCapital] = None
    stockCapital: Optional[StockCapital] = None


class FiscalYear(BaseModel):
    isFirst: Optional[bool] = None
    calendarTypeId: Optional[int] = None
    calendarTypeName: Optional[str] = None
    endMonth: Optional[int] = None
    endDay: Optional[int] = None
    endYear: Optional[int] = None


class Guardian(BaseModel):
    name: Optional[str] = None
    identity: Optional[Identity] = None
    nationality: Optional[Nationality] = None
    isFatherGuardian: Optional[bool] = None


class Partnership(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class PartnerShare(BaseModel):
    cashContributionCount: Optional[int] = None
    inKindContributionCount: Optional[int] = None
    totalContributionCount: Optional[int] = None


class PartnerProfitLossDistribution(BaseModel):
    profitDistribution: Optional[float] = None
    lossDistribution: Optional[float] = None


class Party(BaseModel):
    name: Optional[str] = None
    typeId: Optional[int] = None
    typeName: Optional[str] = None
    identity: Optional[Identity] = None
    partnership: Optional[List[Partnership]] = None
    partnerShare: Optional[PartnerShare] = None
    partnerProfitLossDistribution: Optional[PartnerProfitLossDistribution] = None
    nationality: Optional[Nationality] = None
    crNumber: Optional[str] = None
    licenseNo: Optional[str] = None
    guardian: Optional[Guardian] = None


class Position(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Manager(BaseModel):
    name: Optional[str] = None
    typeId: Optional[int] = None
    typeName: Optional[str] = None
    isLicensed: Optional[bool] = None
    identity: Optional[Identity] = None
    nationality: Optional[Nationality] = None
    positions: Optional[List[Position]] = None


class Permission(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    canIssuePOA: Optional[bool] = None
    canDelegate: Optional[bool] = None
    specialConditionText: Optional[str] = None
    exerciseMethodId: Optional[int] = None
    exerciseMethodDescription: Optional[str] = None


class ManagerWithPermissions(Manager):
    permissions: Optional[List[Permission]] = None


class ManagementBoard(BaseModel):
    meetingQuorumId: Optional[int] = None
    meetingQuorumName: Optional[str] = None
    canDelegateAttendance: Optional[bool] = None
    termYears: Optional[int] = None
    wayOfWork: Optional[str] = None
    meetingPlace: Optional[str] = None
    additionalText: Optional[str] = None
    positions: Optional[List[Position]] = None


class Reward(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class DirectorsBoard(BaseModel):
    memberCount: Optional[int] = None
    termYears: Optional[int] = None
    value: Optional[int] = None
    valueMax: Optional[int] = None
    wayOfWork: Optional[str] = None
    meetingPlace: Optional[str] = None
    meetingQuorum: Optional[int] = None
    meetingLegalQuorum: Optional[int] = None
    canDelegateAttendance: Optional[bool] = None
    boardCallMechanism: Optional[str] = None
    membershipExpiryTerms: Optional[str] = None
    additionalText: Optional[str] = None
    rewards: Optional[List[Reward]] = None
    positions: Optional[List[Position]] = None


class Management(BaseModel):
    structureId: Optional[int] = None
    structureName: Optional[str] = None
    dismissalMethod: Optional[str] = None
    managers: Optional[List[Manager]] = None
    managementBoard: Optional[ManagementBoard] = None
    directorsBoard: Optional[DirectorsBoard] = None


class Activity(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class Entity(BaseModel):
    crNationalNumber: Optional[str] = None
    crNumber: Optional[str] = None
    name: Optional[str] = None
    nameLangId: Optional[int] = None
    nameLangDesc: Optional[str] = None
    companyDuration: Optional[int] = None
    headquarterCityId: Optional[int] = None
    headquarterCityName: Optional[str] = None
    isLicenseBased: Optional[bool] = None
    licenseIssuerNationalNo: Optional[str] = None
    licenseIssuerName: Optional[str] = None
    entityType: Optional[EntityType] = None
    capital: Optional[Capital] = None
    fiscalYear: Optional[FiscalYear] = None
    parties: Optional[List[Party]] = None
    management: Optional[Management] = None
    activities: Optional[List[Activity]] = None


class NotificationChannel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class PartnerDecision(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    approvePercentage: Optional[str] = None
    approveAdditionalText: Optional[str] = None


class ProfitAllocation(BaseModel):
    percentage: Optional[int] = None
    purpose: Optional[str] = None


class SetAsideDetails(BaseModel):
    isSetAsideEnabled: Optional[bool] = None
    profitAllocation: Optional[ProfitAllocation] = None


class Article(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    partId: Optional[int] = None
    partName: Optional[str] = None


class AdditionalArticle(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    partId: Optional[int] = None
    partName: Optional[str] = None


class CompanyContractInfo(BaseModel):
    contractCopyNumber: Optional[int] = None
    contractDate: Optional[str] = None
    entity: Optional[Entity] = None
    notificationChannel: Optional[List[NotificationChannel]] = None
    partnerDecision: Optional[List[PartnerDecision]] = None
    additionalDecisionText: Optional[str] = None
    setAsideDetails: Optional[SetAsideDetails] = None
    articles: Optional[List[Article]] = None
    additionalArticles: Optional[List[AdditionalArticle]] = None


class ManagementResponse(Management):
    pass


# ManagerResponse is just a list of ManagerWithPermissions
ManagerResponse = List[ManagerWithPermissions]


class Lookup(BaseModel):
    id: Optional[int] = None
    nameAr: Optional[str] = None
    nameEn: Optional[str] = None


class ErrorResponse(BaseModel):
    code: Optional[str] = None
    message: Optional[str] = None
