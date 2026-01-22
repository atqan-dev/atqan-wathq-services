"""
CRUD operations for Power of Attorney.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.wathq_power_of_attorney import PowerOfAttorney
from app.schemas.wathq_power_of_attorney import PowerOfAttorneyCreate, PowerOfAttorneyUpdate


class CRUDPowerOfAttorney(CRUDBase[PowerOfAttorney, PowerOfAttorneyCreate, PowerOfAttorneyUpdate]):
    """CRUD operations for Power of Attorney"""
    
    def get_with_relations(self, db: Session, *, id: int) -> Optional[PowerOfAttorney]:
        """
        Get a power of attorney by ID with all related data eagerly loaded.
        """
        return db.query(PowerOfAttorney).options(
            joinedload(PowerOfAttorney.allowed_actors),
            joinedload(PowerOfAttorney.principals),
            joinedload(PowerOfAttorney.agents),
            joinedload(PowerOfAttorney.text_list_items)
        ).filter(PowerOfAttorney.id == id).first()
    
    def get_by_code(self, db: Session, *, code: str) -> Optional[PowerOfAttorney]:
        """
        Get a power of attorney by code.
        """
        return db.query(PowerOfAttorney).filter(PowerOfAttorney.code == code).first()
    
    def get_multi_with_relations(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[PowerOfAttorney]:
        """
        Get multiple power of attorney records with all related data eagerly loaded.
        """
        return db.query(PowerOfAttorney).options(
            joinedload(PowerOfAttorney.allowed_actors),
            joinedload(PowerOfAttorney.principals),
            joinedload(PowerOfAttorney.agents),
            joinedload(PowerOfAttorney.text_list_items)
        ).offset(skip).limit(limit).all()


power_of_attorney = CRUDPowerOfAttorney(PowerOfAttorney)
