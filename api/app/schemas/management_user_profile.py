"""
Pydantic schemas for management user profile operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ManagementUserProfileBase(BaseModel):
    fullname: Optional[str] = None
    address: Optional[str] = None
    mobile: Optional[str] = None
    city: Optional[str] = None
    company_name: Optional[str] = None
    commercial_registration_number: Optional[str] = None
    entity_number: Optional[str] = None
    full_info: Optional[Dict[str, Any]] = None
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    avatar_image_url: Optional[str] = None
    is_active: Optional[bool] = True


class ManagementUserProfileCreate(ManagementUserProfileBase):
    management_user_id: Optional[int] = None
    fullname: Optional[str] = None
    address: Optional[str] = None
    mobile: Optional[str] = None
    city: Optional[str] = None
    company_name: Optional[str] = None
    commercial_registration_number: Optional[str] = None
    entity_number: Optional[str] = None
    email: Optional[str] = None
    avatar_image_url: Optional[str] = None


class ManagementUserProfileUpdate(ManagementUserProfileBase):
    pass


class ManagementUserProfileInDBBase(ManagementUserProfileBase):
    id: Optional[int] = None
    management_user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ManagementUserProfile(ManagementUserProfileInDBBase):
    pass


class ManagementUserProfileInDB(ManagementUserProfileInDBBase):
    pass


class AvatarUpdate(BaseModel):
    avatar_image_url: str
