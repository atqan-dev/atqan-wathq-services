"""
Capital Info model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CapitalInfo(Base):
    """
    Capital Info model representing capital information for commercial registrations.
    """

    __tablename__ = "capital_info"
    __table_args__ = {'schema': 'wathq'}

    cr_number = Column(String(20), ForeignKey('wathq.commercial_registrations.cr_number'), primary_key=True)
    currency_id = Column(Integer, nullable=True)
    currency_name = Column(String(50), nullable=True)
    
    contrib_type_id = Column(Integer, nullable=True)
    contrib_type_name = Column(String(50), nullable=True)
    contrib_cash = Column(Numeric(15, 2), nullable=True)
    contrib_in_kind = Column(Numeric(15, 2), nullable=True)
    contrib_value = Column(Numeric(15, 2), nullable=True)
    total_cash_contribution = Column(Numeric(15, 2), nullable=True)
    total_in_kind_contribution = Column(Numeric(15, 2), nullable=True)

    stock_type_id = Column(Integer, nullable=True)
    stock_type_name = Column(String(50), nullable=True)
    stock_capital = Column(Numeric(15, 2), nullable=True)
    stock_announced_capital = Column(Numeric(15, 2), nullable=True)
    stock_paid_capital = Column(Numeric(15, 2), nullable=True)
    stock_cash_capital = Column(Numeric(15, 2), nullable=True)
    stock_in_kind_capital = Column(Numeric(15, 2), nullable=True)

    commercial_registration = relationship("CommercialRegistration", back_populates="capital_info")
