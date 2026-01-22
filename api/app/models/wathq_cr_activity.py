"""
CR Activity model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CRActivity(Base):
    """
    CR Activity model representing commercial registration activities.
    """

    __tablename__ = "cr_activities"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cr_number = Column(String(20), nullable=False)
    cr_id = Column(Integer, ForeignKey('wathq.commercial_registrations.id'), nullable=False, index=True)
    activity_id = Column(String(20), nullable=True)
    activity_name = Column(String(255), nullable=True)

    commercial_registration = relationship("CommercialRegistration", back_populates="activities")
