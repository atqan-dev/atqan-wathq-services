"""
CR Liquidator Position model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CRLiquidatorPosition(Base):
    """
    CR Liquidator Position model representing liquidator positions.
    """

    __tablename__ = "cr_liquidator_positions"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    liquidator_id = Column(Integer, ForeignKey('wathq.cr_liquidators.id'), nullable=False)
    position_id = Column(Integer, nullable=True)
    position_name = Column(String(100), nullable=True)

    liquidator = relationship("CRLiquidator", back_populates="positions")
