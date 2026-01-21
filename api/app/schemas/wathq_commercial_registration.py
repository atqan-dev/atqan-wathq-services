"""
Pydantic schemas for Commercial Registration.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel


class CapitalInfoBase(BaseModel):
    currency_id: Optional[int] = None
    currency_name: Optional[str] = None
    contrib_type_id: Optional[int] = None
    contrib_type_name: Optional[str] = None
    contrib_cash: Optional[Decimal] = None
    contrib_in_kind: Optional[Decimal] = None
    contrib_value: Optional[Decimal] = None
    total_cash_contribution: Optional[Decimal] = None
    total_in_kind_contribution: Optional[Decimal] = None
    stock_type_id: Optional[int] = None
    stock_type_name: Optional[str] = None
    stock_capital: Optional[Decimal] = None
    stock_announced_capital: Optional[Decimal] = None
    stock_paid_capital: Optional[Decimal] = None
    stock_cash_capital: Optional[Decimal] = None
    stock_in_kind_capital: Optional[Decimal] = None


class CapitalInfoCreate(CapitalInfoBase):
    cr_number: str


class CapitalInfoUpdate(CapitalInfoBase):
    pass


class CapitalInfo(CapitalInfoBase):
    cr_number: Optional[str] = None

    class Config:
        from_attributes = True


class CREntityCharacterBase(BaseModel):
    character_id: Optional[int] = None
    character_name: Optional[str] = None


class CREntityCharacterCreate(CREntityCharacterBase):
    cr_number: str


class CREntityCharacterUpdate(CREntityCharacterBase):
    pass


class CREntityCharacter(CREntityCharacterBase):
    id: int
    cr_number: Optional[str] = None

    class Config:
        from_attributes = True


class CRActivityBase(BaseModel):
    activity_id: Optional[str] = None
    activity_name: Optional[str] = None


class CRActivityCreate(CRActivityBase):
    cr_number: str


class CRActivityUpdate(CRActivityBase):
    pass


class CRActivity(CRActivityBase):
    id: int
    cr_number: Optional[str] = None

    class Config:
        from_attributes = True


class CRStockBase(BaseModel):
    stock_count: Optional[int] = None
    stock_value: Optional[Decimal] = None
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    class_reference_id: Optional[int] = None
    class_name: Optional[str] = None


class CRStockCreate(CRStockBase):
    cr_number: str


class CRStockUpdate(CRStockBase):
    pass


class CRStock(CRStockBase):
    id: int
    cr_number: Optional[str] = None

    class Config:
        from_attributes = True


class CREstoreActivityBase(BaseModel):
    activity_id: Optional[str] = None
    activity_name: Optional[str] = None


class CREstoreActivityCreate(CREstoreActivityBase):
    estore_id: int


class CREstoreActivityUpdate(CREstoreActivityBase):
    pass


class CREstoreActivity(CREstoreActivityBase):
    id: int
    estore_id: int

    class Config:
        from_attributes = True


class CREstoreBase(BaseModel):
    auth_platform_url: Optional[str] = None
    store_url: Optional[str] = None


class CREstoreCreate(CREstoreBase):
    cr_number: str


class CREstoreUpdate(CREstoreBase):
    pass


class CREstore(CREstoreBase):
    id: int
    cr_number: Optional[str] = None
    activities: list[CREstoreActivity] = []

    class Config:
        from_attributes = True


class CRPartyPartnershipBase(BaseModel):
    partnership_id: Optional[int] = None
    partnership_name: Optional[str] = None


class CRPartyPartnershipCreate(CRPartyPartnershipBase):
    party_id: int


class CRPartyPartnershipUpdate(CRPartyPartnershipBase):
    pass


class CRPartyPartnership(CRPartyPartnershipBase):
    id: int
    party_id: int

    class Config:
        from_attributes = True


class CRPartyBase(BaseModel):
    name: Optional[str] = None
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    identity_id: Optional[str] = None
    identity_type_id: Optional[int] = None
    identity_type_name: Optional[str] = None
    share_cash_count: Optional[int] = None
    share_in_kind_count: Optional[int] = None
    share_total_count: Optional[int] = None


class CRPartyCreate(CRPartyBase):
    cr_number: str


class CRPartyUpdate(CRPartyBase):
    pass


class CRParty(CRPartyBase):
    id: int
    cr_number: Optional[str] = None
    partnerships: list[CRPartyPartnership] = []

    class Config:
        from_attributes = True


class CRManagerPositionBase(BaseModel):
    position_id: Optional[int] = None
    position_name: Optional[str] = None


class CRManagerPositionCreate(CRManagerPositionBase):
    manager_id: int


class CRManagerPositionUpdate(CRManagerPositionBase):
    pass


class CRManagerPosition(CRManagerPositionBase):
    id: int
    manager_id: int

    class Config:
        from_attributes = True


class CRManagerBase(BaseModel):
    name: Optional[str] = None
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    is_licensed: Optional[bool] = None
    identity_id: Optional[str] = None
    identity_type_id: Optional[int] = None
    identity_type_name: Optional[str] = None
    nationality_id: Optional[int] = None
    nationality_name: Optional[str] = None


class CRManagerCreate(CRManagerBase):
    cr_number: str


class CRManagerUpdate(CRManagerBase):
    pass


class CRManager(CRManagerBase):
    id: int
    cr_number: Optional[str] = None
    positions: list[CRManagerPosition] = []

    class Config:
        from_attributes = True


class CRLiquidatorPositionBase(BaseModel):
    position_id: Optional[int] = None
    position_name: Optional[str] = None


class CRLiquidatorPositionCreate(CRLiquidatorPositionBase):
    liquidator_id: int


class CRLiquidatorPositionUpdate(CRLiquidatorPositionBase):
    pass


class CRLiquidatorPosition(CRLiquidatorPositionBase):
    id: int
    liquidator_id: int

    class Config:
        from_attributes = True


class CRLiquidatorBase(BaseModel):
    name: Optional[str] = None
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    identity_id: Optional[str] = None
    identity_type_id: Optional[int] = None
    identity_type_name: Optional[str] = None
    nationality_id: Optional[int] = None
    nationality_name: Optional[str] = None


class CRLiquidatorCreate(CRLiquidatorBase):
    cr_number: str


class CRLiquidatorUpdate(CRLiquidatorBase):
    pass


class CRLiquidator(CRLiquidatorBase):
    id: int
    cr_number: Optional[str] = None
    positions: list[CRLiquidatorPosition] = []

    class Config:
        from_attributes = True


class CommercialRegistrationBase(BaseModel):
    cr_national_number: Optional[str] = None
    version_no: Optional[int] = None
    name: Optional[str] = None
    name_lang_id: Optional[int] = None
    name_lang_desc: Optional[str] = None
    cr_capital: Optional[Decimal] = None
    company_duration: Optional[int] = None
    is_main: Optional[bool] = None
    issue_date_gregorian: Optional[date] = None
    issue_date_hijri: Optional[str] = None
    main_cr_national_number: Optional[str] = None
    main_cr_number: Optional[str] = None
    in_liquidation_process: Optional[bool] = None
    has_ecommerce: Optional[bool] = None
    headquarter_city_id: Optional[int] = None
    headquarter_city_name: Optional[str] = None
    is_license_based: Optional[bool] = None
    license_issuer_national_number: Optional[str] = None
    license_issuer_name: Optional[str] = None
    partners_nationality_id: Optional[int] = None
    partners_nationality_name: Optional[str] = None
    entity_type_id: Optional[int] = None
    entity_type_name: Optional[str] = None
    entity_form_id: Optional[int] = None
    entity_form_name: Optional[str] = None
    status_id: Optional[int] = None
    status_name: Optional[str] = None
    confirmation_date_gregorian: Optional[date] = None
    confirmation_date_hijri: Optional[str] = None
    reactivation_date_gregorian: Optional[date] = None
    reactivation_date_hijri: Optional[str] = None
    suspension_date_gregorian: Optional[date] = None
    suspension_date_hijri: Optional[str] = None
    deletion_date_gregorian: Optional[date] = None
    deletion_date_hijri: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_mobile: Optional[str] = None
    contact_email: Optional[str] = None
    contact_website: Optional[str] = None
    fiscal_is_first: Optional[bool] = None
    fiscal_calendar_type_id: Optional[int] = None
    fiscal_calendar_type_name: Optional[str] = None
    fiscal_end_month: Optional[int] = None
    fiscal_end_day: Optional[int] = None
    fiscal_end_year: Optional[int] = None
    mgmt_structure_id: Optional[int] = None
    mgmt_structure_name: Optional[str] = None


class CommercialRegistrationCreate(CommercialRegistrationBase):
    cr_number: str


class CommercialRegistrationUpdate(CommercialRegistrationBase):
    pass


class CommercialRegistration(CommercialRegistrationBase):
    id: int
    cr_number: str
    log_id: Optional[UUID] = None
    fetched_at: Optional[datetime] = None
    capital_info: Optional[CapitalInfo] = None
    entity_characters: list[CREntityCharacter] = []
    activities: list[CRActivity] = []
    stocks: list[CRStock] = []
    estores: list[CREstore] = []
    parties: list[CRParty] = []
    managers: list[CRManager] = []
    liquidators: list[CRLiquidator] = []
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    request_body: Optional[Any] = None

    class Config:
        from_attributes = True
