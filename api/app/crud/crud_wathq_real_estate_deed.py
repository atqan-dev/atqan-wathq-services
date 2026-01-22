"""
CRUD operations for Real Estate Deeds.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.wathq_real_estate_deed import Deed
from app.schemas.wathq_real_estate_deed import DeedCreate, DeedUpdate


class CRUDDeed(CRUDBase[Deed, DeedCreate, DeedUpdate]):
    """CRUD operations for Real Estate Deeds"""
    
    def get_with_relations(self, db: Session, *, id: int) -> Optional[Deed]:
        """
        Get a deed by ID with all related data eagerly loaded.
        """
        return db.query(Deed).options(
            joinedload(Deed.owners),
            joinedload(Deed.real_estates)
        ).filter(Deed.id == id).first()
    
    def get_by_deed_number(self, db: Session, *, deed_number: str) -> Optional[Deed]:
        """
        Get a deed by deed number.
        """
        return db.query(Deed).filter(Deed.deed_number == deed_number).first()
    
    def get_by_deed_serial(self, db: Session, *, deed_serial: str) -> Optional[Deed]:
        """
        Get a deed by deed serial.
        """
        return db.query(Deed).filter(Deed.deed_serial == deed_serial).first()
    
    def get_multi_with_relations(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Deed]:
        """
        Get multiple deeds with all related data eagerly loaded.
        """
        return db.query(Deed).options(
            joinedload(Deed.owners),
            joinedload(Deed.real_estates)
        ).offset(skip).limit(limit).all()


deed = CRUDDeed(Deed)
