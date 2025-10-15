"""
CRUD operations for WATHQ offline data.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.crud.base import CRUDBase
from app.models.wathq_offline_data import WathqOfflineData
from app.schemas.wathq_offline_data import WathqOfflineDataCreate, WathqOfflineDataUpdate


class CRUDWathqOfflineData(CRUDBase[WathqOfflineData, WathqOfflineDataCreate, WathqOfflineDataUpdate]):

    def create_offline_data(
        self,
        db: Session,
        *,
        service_id: UUID,
        tenant_id: int,
        fetched_by: int,
        full_external_url: str,
        response_body: Dict[str, Any]
    ) -> WathqOfflineData:
        """Create offline data record."""
        offline_data = WathqOfflineData(
            service_id=service_id,
            tenant_id=tenant_id,
            fetched_by=fetched_by,
            full_external_url=full_external_url,
            response_body=response_body
        )
        db.add(offline_data)
        db.commit()
        db.refresh(offline_data)
        return offline_data

    def get_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[WathqOfflineData]:
        """Get offline data for a specific tenant."""
        return (
            db.query(WathqOfflineData)
            .filter(WathqOfflineData.tenant_id == tenant_id)
            .order_by(desc(WathqOfflineData.fetched_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_service_and_tenant(
        self, db: Session, *, service_id: UUID, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[WathqOfflineData]:
        """Get offline data for specific service and tenant."""
        return (
            db.query(WathqOfflineData)
            .filter(
                and_(
                    WathqOfflineData.service_id == service_id,
                    WathqOfflineData.tenant_id == tenant_id
                )
            )
            .order_by(desc(WathqOfflineData.fetched_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_by_url_pattern(
        self, db: Session, *, tenant_id: int, url_pattern: str, skip: int = 0, limit: int = 100
    ) -> List[WathqOfflineData]:
        """Search offline data by URL pattern."""
        return (
            db.query(WathqOfflineData)
            .filter(
                and_(
                    WathqOfflineData.tenant_id == tenant_id,
                    WathqOfflineData.full_external_url.contains(url_pattern)
                )
            )
            .order_by(desc(WathqOfflineData.fetched_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[WathqOfflineData]:
        """Get all offline data."""
        return db.query(WathqOfflineData).offset(skip).limit(limit).all()


wathq_offline_data = CRUDWathqOfflineData(WathqOfflineData)
