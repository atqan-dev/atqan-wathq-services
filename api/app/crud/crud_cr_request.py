from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.cr_request import CrRequest
from app.schemas.cr_request import CrRequestCreate, CrRequestUpdate


class CRUDCrRequest(CRUDBase[CrRequest, CrRequestCreate, CrRequestUpdate]):
    def get_by_cr_number(
        self, db: Session, *, cr_number: str, skip: int = 0, limit: int = 100
    ) -> List[CrRequest]:
        """Get all requests for a specific CR number"""
        return (
            db.query(self.model)
            .filter(CrRequest.cr_number == cr_number)
            .order_by(desc(CrRequest.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self, db: Session, *, status_number: int, skip: int = 0, limit: int = 100
    ) -> List[CrRequest]:
        """Get all requests with a specific status"""
        return (
            db.query(self.model)
            .filter(CrRequest.status_number == status_number)
            .order_by(desc(CrRequest.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[CrRequest]:
        """Get recent requests ordered by creation date"""
        return (
            db.query(self.model)
            .order_by(desc(CrRequest.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )


cr_request = CRUDCrRequest(CrRequest)
