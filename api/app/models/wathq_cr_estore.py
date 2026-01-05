"""
CR Estore model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CREstore(Base):
    """
    CR Estore model representing e-commerce stores.
    """

    __tablename__ = "cr_estores"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cr_number = Column(String(20), ForeignKey('wathq.commercial_registrations.cr_number'), nullable=False)
    auth_platform_url = Column(String(255), nullable=True)
    store_url = Column(String(255), nullable=True)

    commercial_registration = relationship("CommercialRegistration", back_populates="estores")
    activities = relationship("CREstoreActivity", back_populates="estore")
