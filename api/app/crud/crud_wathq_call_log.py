"""
CRUD operations for WATHQ call logs.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.wathq_call_log import WathqCallLog
from app.schemas.wathq_call_log import WathqCallLogCreate, WathqCallLogUpdate


class CRUDWathqCallLog(CRUDBase[WathqCallLog, WathqCallLogCreate, WathqCallLogUpdate]):

    def get_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[WathqCallLog]:
        """Get call logs for a specific tenant."""
        return (
            db.query(WathqCallLog)
            .filter(WathqCallLog.tenant_id == tenant_id)
            .order_by(desc(WathqCallLog.fetched_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[WathqCallLog]:
        """Get call logs for a specific user."""
        return (
            db.query(WathqCallLog)
            .filter(WathqCallLog.user_id == user_id)
            .order_by(desc(WathqCallLog.fetched_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_service(
        self, db: Session, *, service_slug: str, tenant_id: Optional[int] = None,
        skip: int = 0, limit: int = 100
    ) -> List[WathqCallLog]:
        """Get call logs for a specific service."""
        query = db.query(WathqCallLog).filter(WathqCallLog.service_slug == service_slug)

        if tenant_id:
            query = query.filter(WathqCallLog.tenant_id == tenant_id)

        return (
            query.order_by(desc(WathqCallLog.fetched_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_calls_by_tenant(self, db: Session, *, tenant_id: int) -> int:
        """Count total calls for a tenant."""
        return db.query(WathqCallLog).filter(WathqCallLog.tenant_id == tenant_id).count()

    def count_calls_by_service(
        self, db: Session, *, service_slug: str, tenant_id: Optional[int] = None
    ) -> int:
        """Count calls for a specific service."""
        query = db.query(WathqCallLog).filter(WathqCallLog.service_slug == service_slug)

        if tenant_id:
            query = query.filter(WathqCallLog.tenant_id == tenant_id)

        return query.count()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[WathqCallLog]:
        """Get all call logs."""
        return db.query(WathqCallLog).offset(skip).limit(limit).all()


wathq_call_log = CRUDWathqCallLog(WathqCallLog)
