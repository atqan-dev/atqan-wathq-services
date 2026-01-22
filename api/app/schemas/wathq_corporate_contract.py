"""
Pydantic schemas for Corporate Contract endpoints.
"""

from typing import Optional, List, Any
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# Nested schemas for related data
class ContractStockBase(BaseModel):
    stock_type_name: Optional[str] = None
    stock_count: Optional[int] = None
    stock_value: Optional[Decimal] = None


class ContractStock(ContractStockBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True


class ContractPartyBase(BaseModel):
    name: Optional[str] = None
    type_name: Optional[str] = None
    identity_number: Optional[str] = None
    identity_type: Optional[str] = None
    nationality: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_identity_number: Optional[str] = None
    is_father_guardian: Optional[bool] = None


class ContractParty(ContractPartyBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True


class ContractManagerBase(BaseModel):
    name: Optional[str] = None
    type_name: Optional[str] = None
    is_licensed: Optional[bool] = None
    identity_number: Optional[str] = None
    nationality: Optional[str] = None
    position_name: Optional[str] = None


class ContractManager(ContractManagerBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True


class ContractManagementConfigBase(BaseModel):
    structure_name: Optional[str] = None
    meeting_quorum_name: Optional[str] = None
    can_delegate_attendance: Optional[bool] = None
    term_years: Optional[int] = None


class ContractManagementConfig(ContractManagementConfigBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True


class ContractActivityBase(BaseModel):
    activity_id: Optional[str] = None
    activity_name: Optional[str] = None


class ContractActivity(ContractActivityBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True


class ContractArticleBase(BaseModel):
    original_id: Optional[int] = None
    article_text: Optional[str] = None
    part_name: Optional[str] = None


class ContractArticle(ContractArticleBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True


class ContractDecisionBase(BaseModel):
    decision_name: Optional[str] = None
    approve_percentage: Optional[Decimal] = None


class ContractDecision(ContractDecisionBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True


class NotificationChannelBase(BaseModel):
    channel_name: Optional[str] = None


class NotificationChannel(NotificationChannelBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True


# Main Corporate Contract schemas
class CorporateContractBase(BaseModel):
    contract_id: Optional[int] = None
    contract_copy_number: Optional[int] = None
    contract_date: Optional[date] = None
    
    # Entity Details
    cr_national_number: Optional[str] = None
    cr_number: Optional[str] = None
    entity_name: Optional[str] = None
    entity_name_lang_desc: Optional[str] = None
    company_duration: Optional[int] = None
    headquarter_city_name: Optional[str] = None
    is_license_based: Optional[bool] = None
    entity_type_name: Optional[str] = None
    entity_form_name: Optional[str] = None
    
    # Fiscal Year
    fiscal_calendar_type: Optional[str] = None
    fiscal_year_end_month: Optional[int] = None
    fiscal_year_end_day: Optional[int] = None
    fiscal_year_end_year: Optional[int] = None
    
    # Capital Summary
    currency_name: Optional[str] = None
    total_capital: Optional[Decimal] = None
    paid_capital: Optional[Decimal] = None
    cash_capital: Optional[Decimal] = None
    in_kind_capital: Optional[Decimal] = None
    
    # Set Aside / Profit Allocation
    is_set_aside_enabled: Optional[bool] = None
    profit_allocation_percentage: Optional[Decimal] = None
    profit_allocation_purpose: Optional[str] = None
    additional_decision_text: Optional[str] = None


class CorporateContractCreate(CorporateContractBase):
    pass


class CorporateContractUpdate(CorporateContractBase):
    pass


class CorporateContract(CorporateContractBase):
    id: int
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    request_body: Optional[Any] = None
    
    # Nested relationships
    stocks: List[ContractStock] = []
    parties: List[ContractParty] = []
    managers: List[ContractManager] = []
    management_config: Optional[ContractManagementConfig] = None
    activities: List[ContractActivity] = []
    articles: List[ContractArticle] = []
    decisions: List[ContractDecision] = []
    notification_channels: List[NotificationChannel] = []

    class Config:
        from_attributes = True
