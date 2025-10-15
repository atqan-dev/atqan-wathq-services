"""
WATHQ utilities for tenant-specific API key management.
"""

from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.service import TenantService, Service


def get_tenant_wathq_key(
    db: Session, 
    tenant_id: int, 
    service_id: UUID
) -> Optional[str]:
    """
    Get the WATHQ API key for a specific tenant and service.
    """
    tenant_service = (
        db.query(TenantService)
        .filter(
            TenantService.tenant_id == tenant_id,
            TenantService.service_id == service_id,
            TenantService.is_active == True,
            TenantService.is_approved == True
        )
        .first()
    )
    
    return tenant_service.wathq_api_key if tenant_service else None


def get_tenant_wathq_key_by_slug(
    db: Session, 
    tenant_id: int, 
    service_slug: str
) -> Optional[str]:
    """
    Get the WATHQ API key for a specific tenant and service by slug.
    """
    tenant_service = (
        db.query(TenantService)
        .join(Service)
        .filter(
            TenantService.tenant_id == tenant_id,
            Service.slug == service_slug,
            TenantService.is_active == True,
            TenantService.is_approved == True
        )
        .first()
    )
    
    return tenant_service.wathq_api_key if tenant_service else None


def get_service_id_by_slug(db: Session, service_slug: str) -> Optional[UUID]:
    """
    Get service ID by slug.
    """
    service = db.query(Service).filter(Service.slug == service_slug).first()
    return service.id if service else None