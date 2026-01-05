"""
CRUD operations for Commercial Registration and related models.
"""

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.wathq_commercial_registration import CommercialRegistration
from app.models.wathq_capital_info import CapitalInfo
from app.models.wathq_cr_activity import CRActivity
from app.models.wathq_cr_entity_character import CREntityCharacter
from app.models.wathq_cr_estore import CREstore
from app.models.wathq_cr_estore_activity import CREstoreActivity
from app.models.wathq_cr_liquidator import CRLiquidator
from app.models.wathq_cr_liquidator_position import CRLiquidatorPosition
from app.models.wathq_cr_manager import CRManager
from app.models.wathq_cr_manager_position import CRManagerPosition
from app.models.wathq_cr_party import CRParty
from app.models.wathq_cr_party_partnership import CRPartyPartnership
from app.models.wathq_cr_stock import CRStock
from app.schemas.wathq_commercial_registration import (
    CommercialRegistrationCreate,
    CommercialRegistrationUpdate,
)


class CRUDCommercialRegistration(
    CRUDBase[CommercialRegistration, CommercialRegistrationCreate, CommercialRegistrationUpdate]
):
    def get_by_cr_number(
        self, db: Session, *, cr_number: str
    ) -> Optional[CommercialRegistration]:
        """Get commercial registration by CR number with all related data."""
        return (
            db.query(CommercialRegistration)
            .options(
                joinedload(CommercialRegistration.capital_info),
                joinedload(CommercialRegistration.entity_characters),
                joinedload(CommercialRegistration.activities),
                joinedload(CommercialRegistration.stocks),
                joinedload(CommercialRegistration.estores).joinedload(CREstore.activities),
                joinedload(CommercialRegistration.parties).joinedload(CRParty.partnerships),
                joinedload(CommercialRegistration.managers).joinedload(CRManager.positions),
                joinedload(CommercialRegistration.liquidators).joinedload(CRLiquidator.positions),
            )
            .filter(CommercialRegistration.cr_number == cr_number)
            .first()
        )

    def get_multi_with_relations(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[CommercialRegistration]:
        """Get multiple commercial registrations with all related data."""
        return (
            db.query(CommercialRegistration)
            .options(
                joinedload(CommercialRegistration.capital_info),
                joinedload(CommercialRegistration.entity_characters),
                joinedload(CommercialRegistration.activities),
                joinedload(CommercialRegistration.stocks),
                joinedload(CommercialRegistration.estores).joinedload(CREstore.activities),
                joinedload(CommercialRegistration.parties).joinedload(CRParty.partnerships),
                joinedload(CommercialRegistration.managers).joinedload(CRManager.positions),
                joinedload(CommercialRegistration.liquidators).joinedload(CRLiquidator.positions),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_by_name(
        self, db: Session, *, name: str, skip: int = 0, limit: int = 100
    ) -> list[CommercialRegistration]:
        """Search commercial registrations by name."""
        return (
            db.query(CommercialRegistration)
            .filter(CommercialRegistration.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, db: Session, *, status_id: int, skip: int = 0, limit: int = 100
    ) -> list[CommercialRegistration]:
        """Get commercial registrations by status."""
        return (
            db.query(CommercialRegistration)
            .filter(CommercialRegistration.status_id == status_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_city(
        self, db: Session, *, city_id: int, skip: int = 0, limit: int = 100
    ) -> list[CommercialRegistration]:
        """Get commercial registrations by headquarter city."""
        return (
            db.query(CommercialRegistration)
            .filter(CommercialRegistration.headquarter_city_id == city_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDCapitalInfo(CRUDBase[CapitalInfo, dict, dict]):
    pass


class CRUDCREntityCharacter(CRUDBase[CREntityCharacter, dict, dict]):
    def get_by_cr_number(
        self, db: Session, *, cr_number: str
    ) -> list[CREntityCharacter]:
        """Get all entity characters for a CR number."""
        return (
            db.query(CREntityCharacter)
            .filter(CREntityCharacter.cr_number == cr_number)
            .all()
        )


class CRUDCRActivity(CRUDBase[CRActivity, dict, dict]):
    def get_by_cr_number(self, db: Session, *, cr_number: str) -> list[CRActivity]:
        """Get all activities for a CR number."""
        return db.query(CRActivity).filter(CRActivity.cr_number == cr_number).all()


class CRUDCRStock(CRUDBase[CRStock, dict, dict]):
    def get_by_cr_number(self, db: Session, *, cr_number: str) -> list[CRStock]:
        """Get all stocks for a CR number."""
        return db.query(CRStock).filter(CRStock.cr_number == cr_number).all()


class CRUDCREstore(CRUDBase[CREstore, dict, dict]):
    def get_by_cr_number(self, db: Session, *, cr_number: str) -> list[CREstore]:
        """Get all estores for a CR number."""
        return (
            db.query(CREstore)
            .options(joinedload(CREstore.activities))
            .filter(CREstore.cr_number == cr_number)
            .all()
        )


class CRUDCREstoreActivity(CRUDBase[CREstoreActivity, dict, dict]):
    def get_by_estore_id(
        self, db: Session, *, estore_id: int
    ) -> list[CREstoreActivity]:
        """Get all activities for an estore."""
        return (
            db.query(CREstoreActivity)
            .filter(CREstoreActivity.estore_id == estore_id)
            .all()
        )


class CRUDCRParty(CRUDBase[CRParty, dict, dict]):
    def get_by_cr_number(self, db: Session, *, cr_number: str) -> list[CRParty]:
        """Get all parties for a CR number."""
        return (
            db.query(CRParty)
            .options(joinedload(CRParty.partnerships))
            .filter(CRParty.cr_number == cr_number)
            .all()
        )


class CRUDCRPartyPartnership(CRUDBase[CRPartyPartnership, dict, dict]):
    def get_by_party_id(
        self, db: Session, *, party_id: int
    ) -> list[CRPartyPartnership]:
        """Get all partnerships for a party."""
        return (
            db.query(CRPartyPartnership)
            .filter(CRPartyPartnership.party_id == party_id)
            .all()
        )


class CRUDCRManager(CRUDBase[CRManager, dict, dict]):
    def get_by_cr_number(self, db: Session, *, cr_number: str) -> list[CRManager]:
        """Get all managers for a CR number."""
        return (
            db.query(CRManager)
            .options(joinedload(CRManager.positions))
            .filter(CRManager.cr_number == cr_number)
            .all()
        )


class CRUDCRManagerPosition(CRUDBase[CRManagerPosition, dict, dict]):
    def get_by_manager_id(
        self, db: Session, *, manager_id: int
    ) -> list[CRManagerPosition]:
        """Get all positions for a manager."""
        return (
            db.query(CRManagerPosition)
            .filter(CRManagerPosition.manager_id == manager_id)
            .all()
        )


class CRUDCRLiquidator(CRUDBase[CRLiquidator, dict, dict]):
    def get_by_cr_number(self, db: Session, *, cr_number: str) -> list[CRLiquidator]:
        """Get all liquidators for a CR number."""
        return (
            db.query(CRLiquidator)
            .options(joinedload(CRLiquidator.positions))
            .filter(CRLiquidator.cr_number == cr_number)
            .all()
        )


class CRUDCRLiquidatorPosition(CRUDBase[CRLiquidatorPosition, dict, dict]):
    def get_by_liquidator_id(
        self, db: Session, *, liquidator_id: int
    ) -> list[CRLiquidatorPosition]:
        """Get all positions for a liquidator."""
        return (
            db.query(CRLiquidatorPosition)
            .filter(CRLiquidatorPosition.liquidator_id == liquidator_id)
            .all()
        )


commercial_registration = CRUDCommercialRegistration(CommercialRegistration)
capital_info = CRUDCapitalInfo(CapitalInfo)
cr_entity_character = CRUDCREntityCharacter(CREntityCharacter)
cr_activity = CRUDCRActivity(CRActivity)
cr_stock = CRUDCRStock(CRStock)
cr_estore = CRUDCREstore(CREstore)
cr_estore_activity = CRUDCREstoreActivity(CREstoreActivity)
cr_party = CRUDCRParty(CRParty)
cr_party_partnership = CRUDCRPartyPartnership(CRPartyPartnership)
cr_manager = CRUDCRManager(CRManager)
cr_manager_position = CRUDCRManagerPosition(CRManagerPosition)
cr_liquidator = CRUDCRLiquidator(CRLiquidator)
cr_liquidator_position = CRUDCRLiquidatorPosition(CRLiquidatorPosition)
