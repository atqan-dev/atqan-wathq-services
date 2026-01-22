"""
CR Manager model for Wathq schema.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CRManager(Base):
    """
    CR Manager model representing managers in commercial registrations.
    """

    __tablename__ = "cr_managers"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cr_number = Column(String(20), nullable=False)
    cr_id = Column(Integer, ForeignKey('wathq.commercial_registrations.id'), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    type_id = Column(Integer, nullable=True)
    type_name = Column(String(100), nullable=True)
    is_licensed = Column(Boolean, nullable=True)
    identity_id = Column(String(50), nullable=True)
    identity_type_id = Column(Integer, nullable=True)
    identity_type_name = Column(String(50), nullable=True)
    nationality_id = Column(Integer, nullable=True)
    nationality_name = Column(String(100), nullable=True)

    commercial_registration = relationship("CommercialRegistration", back_populates="managers")
    positions = relationship("CRManagerPosition", back_populates="manager")
