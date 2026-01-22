from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID


class CsRequestBase(BaseModel):
    url: str = Field(..., max_length=500)
    cr_number: str = Field(..., max_length=50)
    language: str = Field(..., max_length=10)
    response: Optional[Any] = None
    status_number: Optional[int] = None
    status_text: Optional[str] = Field(None, max_length=100)


class CsRequestCreate(CsRequestBase):
    created_by: Optional[str] = Field(None, max_length=100)


class CsRequestUpdate(BaseModel):
    url: Optional[str] = Field(None, max_length=500)
    cr_number: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    response: Optional[Any] = None
    status_number: Optional[int] = None
    status_text: Optional[str] = Field(None, max_length=100)
    updated_by: Optional[str] = Field(None, max_length=100)


class CsRequest(CsRequestBase):
    id: UUID
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
