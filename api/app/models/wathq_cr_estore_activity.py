"""
CR Estore Activity model for Wathq schema.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CREstoreActivity(Base):
    """
    CR Estore Activity model representing e-store activities.
    """

    __tablename__ = "cr_estore_activities"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    estore_id = Column(Integer, ForeignKey('wathq.cr_estores.id'), nullable=False)
    activity_id = Column(String(20), nullable=True)
    activity_name = Column(String(255), nullable=True)

    estore = relationship("CREstore", back_populates="activities")
