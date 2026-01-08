"""
CRUD operations for National Addresses.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.wathq_national_address import Address
from app.schemas.wathq_national_address import AddressCreate, AddressUpdate


class CRUDAddress(CRUDBase[Address, AddressCreate, AddressUpdate]):
    """CRUD operations for National Addresses"""
    
    def get(self, db: Session, id: str) -> Optional[Address]:
        """
        Get an address by pk_address_id.
        """
        return db.query(Address).filter(Address.pk_address_id == id).first()
    
    def get_by_post_code(self, db: Session, *, post_code: str) -> List[Address]:
        """
        Get addresses by post code.
        """
        return db.query(Address).filter(Address.post_code == post_code).all()
    
    def get_by_city(self, db: Session, *, city: str) -> List[Address]:
        """
        Get addresses by city.
        """
        return db.query(Address).filter(Address.city == city).all()
    
    def get_by_region(self, db: Session, *, region_id: str) -> List[Address]:
        """
        Get addresses by region ID.
        """
        return db.query(Address).filter(Address.region_id == region_id).all()
    
    def get_primary_addresses(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Address]:
        """
        Get all primary addresses.
        """
        return db.query(Address).filter(
            Address.is_primary_address == True
        ).offset(skip).limit(limit).all()


address = CRUDAddress(Address)
