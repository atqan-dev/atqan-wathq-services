"""
Pydantic schemas for Wathq Attorney API.
"""

from typing import List, Optional
from pydantic import BaseModel


class AttorneyControl(BaseModel):
    id: int
    controlLable: str
    attorneyTypeName: str
    childControls: List['AttorneyControl'] = []


class LookupResponse(BaseModel):
    id: int
    controlLable: str
    attorneyTypeName: str
    childControls: List[AttorneyControl] = []


class Location(BaseModel):
    id: int
    name: str


class AllowedToActOnBehalf(BaseModel):
    IdentityNo: str
    SocialTypeID: int
    SocialTypeName: str
    Name: str
    Type: int
    TypeName: str
    TypeNameEn: str
    SefaID: int
    SefaName: str
    NationalNumber: Optional[int] = None
    CRNumber: Optional[int] = None
    KararNumber: Optional[int] = None
    MalakiNumber: Optional[int] = None
    DocumentTypeName: Optional[str] = None
    CompanyRepresentTypeID: Optional[int] = None
    CompanyRepresentTypeName: Optional[str] = None
    SakkNumber: Optional[int] = None


class Principal(BaseModel):
    id: str
    name: str
    birthday: str
    SefaId: int
    SefaName: str


class Agent(BaseModel):
    id: str
    name: str
    birthday: str
    SefaId: int
    SefaName: str


class AgentsBehavior(BaseModel):
    ar: str
    en: str


class TextListItem(BaseModel):
    id: int
    text: str
    type: Optional[str] = None


class AttorneyInfoResponse(BaseModel):
    attorneyNumber: int
    status: str
    expiryDate: str
    attorneyType: str
    location: Optional[Location] = None
    AllowedToActOnBehalf: List[AllowedToActOnBehalf]
    principals: List[Principal]
    agents: List[Agent]
    agentsBehavior: AgentsBehavior
    attorneyText: str
    textList: List[TextListItem]


# Update forward references
AttorneyControl.model_rebuild()