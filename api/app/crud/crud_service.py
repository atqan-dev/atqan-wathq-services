"""
CRUD operations for Service model with WATHQ integration.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.service import Service, TenantService
from app.models.user import User
from app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    TenantServiceCreate,
    TenantServiceUpdate,
)


class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Service]:
        return db.query(Service).filter(Service.slug == slug).first()

    def get_wathq_services(self, db: Session) -> List[Service]:
        return (
            db.query(Service)
            .filter(and_(Service.is_active == True, Service.category == "wathq"))
            .all()
        )

    def get_user_authorized_services(
        self, db: Session, *, user_id: int
    ) -> List[Service]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return user.authorized_services

    def assign_service_to_user(
        self, db: Session, *, user_id: int, service_id: UUID
    ) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        service = db.query(Service).filter(Service.id == service_id).first()

        if user and service and service not in user.authorized_services:
            user.authorized_services.append(service)
            db.commit()
            return True
        return False

    def revoke_service_from_user(
        self, db: Session, *, user_id: int, service_id: UUID
    ) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        service = db.query(Service).filter(Service.id == service_id).first()

        if user and service and service in user.authorized_services:
            user.authorized_services.remove(service)
            db.commit()
            return True
        return False


class CRUDTenantService(
    CRUDBase[TenantService, TenantServiceCreate, TenantServiceUpdate]
):
    def get_by_tenant_and_service(
        self, db: Session, *, tenant_id: int, service_id: UUID
    ) -> Optional[TenantService]:
        return (
            db.query(TenantService)
            .filter(
                TenantService.tenant_id == tenant_id,
                TenantService.service_id == service_id,
            )
            .first()
        )

    def get_tenant_services(
        self, db: Session, *, tenant_id: int, approved_only: bool = True
    ) -> List[TenantService]:
        query = (
            db.query(TenantService)
            .options(joinedload(TenantService.service))
            .filter(
                and_(
                    TenantService.tenant_id == tenant_id,
                    TenantService.is_active == True,
                )
            )
        )
        if approved_only:
            query = query.filter(TenantService.is_approved == True)
        return query.all()

    def request_tenant_service(
        self,
        db: Session,
        *,
        tenant_id: int,
        service_id: UUID,
        max_users: int = 10,
        wathq_api_key: str,
    ) -> TenantService:
        existing = self.get_by_tenant_and_service(
            db, tenant_id=tenant_id, service_id=service_id
        )
        if existing:
            existing.is_active = True
            existing.max_users = max_users
            existing.wathq_api_key = wathq_api_key
            db.commit()
            db.refresh(existing)
            return existing

        tenant_service = TenantService(
            tenant_id=tenant_id,
            service_id=service_id,
            max_users=max_users,
            wathq_api_key=wathq_api_key,
            is_active=True,
            is_approved=False,
        )
        db.add(tenant_service)
        db.commit()
        db.refresh(tenant_service)
        return tenant_service

    def approve_tenant_service(
        self, db: Session, *, tenant_service_id: int, approved_by: int
    ) -> Optional[TenantService]:
        tenant_service = (
            db.query(TenantService)
            .filter(TenantService.id == tenant_service_id)
            .first()
        )
        if tenant_service:
            tenant_service.is_approved = True
            tenant_service.approved_by = approved_by
            from sqlalchemy.sql import func

            tenant_service.approved_at = func.now()
            db.commit()
            db.refresh(tenant_service)
            return tenant_service
        return None

    def get_pending_approvals(
        self, db: Session, *, tenant_id: Optional[int] = None
    ) -> List[TenantService]:
        query = (
            db.query(TenantService)
            .options(joinedload(TenantService.service))
            .filter(
                and_(
                    TenantService.is_active == True, TenantService.is_approved == False
                )
            )
        )
        if tenant_id:
            query = query.filter(TenantService.tenant_id == tenant_id)
        return query.all()

    def get_active_services_by_tenant(
        self, db: Session, *, tenant_id: int
    ) -> List[TenantService]:
        return (
            db.query(TenantService).filter(TenantService.tenant_id == tenant_id).all()
        )

    def get_management_all_services(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TenantService]:
        return (
            db.query(TenantService)
            .options(joinedload(TenantService.service))
            .order_by(TenantService.registered_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


service = CRUDService(Service)
tenant_service = CRUDTenantService(TenantService)
