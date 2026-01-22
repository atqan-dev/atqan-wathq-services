"""
CR Entity Character model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CREntityCharacter(Base):
    """
    CR Entity Character model representing entity characteristics.
    """

    __tablename__ = "cr_entity_characters"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cr_number = Column(String(20), nullable=False)
    cr_id = Column(Integer, ForeignKey('wathq.commercial_registrations.id'), nullable=False, index=True)
    character_id = Column(Integer, nullable=True)
    character_name = Column(String(100), nullable=True)

    commercial_registration = relationship("CommercialRegistration", back_populates="entity_characters")
