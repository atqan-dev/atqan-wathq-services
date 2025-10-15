"""
Management User Profile database model for additional company information.
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base


class ManagementUserProfile(Base):
    """
    Management User Profile model for storing additional company and contact information.
    """

    __tablename__ = "management_user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    management_user_id = Column(Integer, ForeignKey("management_users.id"), nullable=False)
    fullname = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    mobile = Column(String, nullable=True)
    city = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    commercial_registration_number = Column(String, nullable=True)
    entity_number = Column(String, nullable=True)
    full_info = Column(JSONB, nullable=True)  # JSON field for additional information
    email = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)
    avatar_image_url = Column(String, nullable=True)  # URL to avatar image
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    management_user = relationship("ManagementUser", backref="profile")
