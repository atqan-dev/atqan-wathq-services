"""
CRUD operations for Corporate Contract.
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.wathq_corporate_contract import CorporateContract
from app.schemas.wathq_corporate_contract import CorporateContractCreate, CorporateContractUpdate


class CRUDCorporateContract(CRUDBase[CorporateContract, CorporateContractCreate, CorporateContractUpdate]):
    def get_with_relations(self, db: Session, *, id: int) -> Optional[CorporateContract]:
        """Get corporate contract with all related data."""
        return db.query(CorporateContract).options(
            joinedload(CorporateContract.stocks),
            joinedload(CorporateContract.parties),
            joinedload(CorporateContract.managers),
            joinedload(CorporateContract.management_config),
            joinedload(CorporateContract.activities),
            joinedload(CorporateContract.articles),
            joinedload(CorporateContract.decisions),
            joinedload(CorporateContract.notification_channels),
        ).filter(CorporateContract.id == id).first()

    def get_multi_with_relations(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[CorporateContract]:
        """Get multiple corporate contracts with all related data."""
        return db.query(CorporateContract).options(
            joinedload(CorporateContract.stocks),
            joinedload(CorporateContract.parties),
            joinedload(CorporateContract.managers),
            joinedload(CorporateContract.management_config),
            joinedload(CorporateContract.activities),
            joinedload(CorporateContract.articles),
            joinedload(CorporateContract.decisions),
            joinedload(CorporateContract.notification_channels),
        ).offset(skip).limit(limit).all()


corporate_contract = CRUDCorporateContract(CorporateContract)
