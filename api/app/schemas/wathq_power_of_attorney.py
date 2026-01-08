"""
Power of Attorney schemas for Wathq.
"""

from typing import List, Optional, Any
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


# PoaAllowedActor Schemas
class PoaAllowedActorBase(BaseModel):
    identity_no: Optional[str] = None
    social_type_id: Optional[int] = None
    social_type_name: Optional[str] = None
    name: Optional[str] = None
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    type_name_en: Optional[str] = None
    sefa_id: Optional[int] = None
    sefa_name: Optional[str] = None
    national_number: Optional[str] = None
    cr_number: Optional[str] = None
    karar_number: Optional[int] = None
    malaki_number: Optional[int] = None
    document_type_name: Optional[str] = None
    company_represent_type_id: Optional[int] = None
    company_represent_type_name: Optional[str] = None
    sakk_number: Optional[int] = None


class PoaAllowedActorCreate(PoaAllowedActorBase):
    poa_id: int


class PoaAllowedActorUpdate(PoaAllowedActorBase):
    pass


class PoaAllowedActor(PoaAllowedActorBase):
    id: int
    poa_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# PoaPrincipal Schemas
class PoaPrincipalBase(BaseModel):
    principal_identity_id: Optional[str] = None
    name: Optional[str] = None
    birthday: Optional[datetime] = None
    sefa_id: Optional[int] = None
    sefa_name: Optional[str] = None


class PoaPrincipalCreate(PoaPrincipalBase):
    poa_id: int


class PoaPrincipalUpdate(PoaPrincipalBase):
    pass


class PoaPrincipal(PoaPrincipalBase):
    id: int
    poa_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# PoaAgent Schemas
class PoaAgentBase(BaseModel):
    agent_identity_id: Optional[str] = None
    name: Optional[str] = None
    birthday: Optional[datetime] = None
    sefa_id: Optional[int] = None
    sefa_name: Optional[str] = None


class PoaAgentCreate(PoaAgentBase):
    poa_id: int


class PoaAgentUpdate(PoaAgentBase):
    pass


class PoaAgent(PoaAgentBase):
    id: int
    poa_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# PoaTextListItem Schemas
class PoaTextListItemBase(BaseModel):
    list_item_id: Optional[int] = None
    text_content: Optional[str] = None
    item_type: Optional[str] = None


class PoaTextListItemCreate(PoaTextListItemBase):
    poa_id: int


class PoaTextListItemUpdate(PoaTextListItemBase):
    pass


class PoaTextListItem(PoaTextListItemBase):
    id: int
    poa_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# PowerOfAttorney Schemas
class PowerOfAttorneyBase(BaseModel):
    code: str
    status: Optional[str] = None
    issue_hijri_date: Optional[str] = None
    issue_greg_date: Optional[date] = None
    expiry_hijri_date: Optional[str] = None
    expiry_greg_date: Optional[date] = None
    attorney_type: Optional[str] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    agents_behavior_ar: Optional[str] = None
    agents_behavior_en: Optional[str] = None
    document_text: Optional[str] = None


class PowerOfAttorneyCreate(PowerOfAttorneyBase):
    pass


class PowerOfAttorneyUpdate(PowerOfAttorneyBase):
    code: Optional[str] = None


class PowerOfAttorney(PowerOfAttorneyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    request_body: Optional[Any] = None
    
    # Nested relationships
    allowed_actors: List[PoaAllowedActor] = []
    principals: List[PoaPrincipal] = []
    agents: List[PoaAgent] = []
    text_list_items: List[PoaTextListItem] = []

    model_config = ConfigDict(from_attributes=True)
