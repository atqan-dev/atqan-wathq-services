"""
CR Party Partnership model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CRPartyPartnership(Base):
    """
    CR Party Partnership model representing partnerships of parties.
    """

    __tablename__ = "cr_party_partnerships"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    party_id = Column(Integer, ForeignKey('wathq.cr_parties.id'), nullable=False)
    partnership_id = Column(Integer, nullable=True)
    partnership_name = Column(String(100), nullable=True)

    party = relationship("CRParty", back_populates="partnerships")
