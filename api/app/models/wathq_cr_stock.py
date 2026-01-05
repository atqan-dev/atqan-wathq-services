"""
CR Stock model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CRStock(Base):
    """
    CR Stock model representing stock information.
    """

    __tablename__ = "cr_stocks"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cr_number = Column(String(20), ForeignKey('wathq.commercial_registrations.cr_number'), nullable=False)
    stock_count = Column(Integer, nullable=True)
    stock_value = Column(Numeric(15, 2), nullable=True)
    type_id = Column(Integer, nullable=True)
    type_name = Column(String(50), nullable=True)
    class_reference_id = Column(Integer, nullable=True)
    class_name = Column(String(50), nullable=True)

    commercial_registration = relationship("CommercialRegistration", back_populates="stocks")
