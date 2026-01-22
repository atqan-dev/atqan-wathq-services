"""
CR Party model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CRParty(Base):
    """
    CR Party model representing parties/partners in commercial registrations.
    """

    __tablename__ = "cr_parties"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cr_number = Column(String(20), nullable=False)
    cr_id = Column(Integer, ForeignKey('wathq.commercial_registrations.id'), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    type_id = Column(Integer, nullable=True)
    type_name = Column(String(100), nullable=True)
    identity_id = Column(String(50), nullable=True)
    identity_type_id = Column(Integer, nullable=True)
    identity_type_name = Column(String(50), nullable=True)
    share_cash_count = Column(Integer, nullable=True)
    share_in_kind_count = Column(Integer, nullable=True)
    share_total_count = Column(Integer, nullable=True)

    commercial_registration = relationship("CommercialRegistration", back_populates="parties")
    partnerships = relationship("CRPartyPartnership", back_populates="party")
