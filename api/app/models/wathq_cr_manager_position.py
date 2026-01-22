"""
CR Manager Position model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CRManagerPosition(Base):
    """
    CR Manager Position model representing manager positions.
    """

    __tablename__ = "cr_manager_positions"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    manager_id = Column(Integer, ForeignKey('wathq.cr_managers.id'), nullable=False)
    position_id = Column(Integer, nullable=True)
    position_name = Column(String(100), nullable=True)

    manager = relationship("CRManager", back_populates="positions")
