"""
Example endpoints showing how to use super admin guards on any route.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.core.guards import require_super_admin, require_management_user
from app import crud

router = APIRouter()


@router.get("/system-stats")
def get_system_stats(
    db: Session = Depends(deps.get_db),
    current_user = Depends(require_super_admin()),
) -> Any:
    """
    Get system statistics (Super Admin only - works with both management and regular super users).
    """
    stats = {
        "total_tenants": len(crud.tenant.get_multi(db)),
        "total_users": len(crud.user.get_multi(db)),
        "total_management_users": len(crud.management_user.get_multi(db)),
        "requester_type": current_user["type"],
        "requester_email": current_user["user"].email,
    }
    return stats


@router.get("/management-only")
def management_only_endpoint(
    db: Session = Depends(deps.get_db),
    current_user = Depends(require_management_user()),
) -> Any:
    """
    Endpoint accessible only to management users.
    """
    return {
        "message": "This endpoint is only accessible to management users",
        "user_email": current_user.email,
        "is_super_admin": current_user.is_super_admin,
    }


@router.post("/dangerous-operation")
def dangerous_operation(
    db: Session = Depends(deps.get_db),
    current_user = Depends(require_super_admin()),
) -> Any:
    """
    Example of a dangerous operation that requires super admin privileges.
    """
    return {
        "message": "Dangerous operation completed",
        "performed_by": current_user["user"].email,
        "user_type": current_user["type"],
        "warning": "This operation should only be performed by super administrators"
    }


@router.get("/tenant-overview")
def get_tenant_overview(
    db: Session = Depends(deps.get_db),
    current_user = Depends(require_management_user()),
) -> Any:
    """
    Get overview of all tenants (Management users only).
    """
    tenants = crud.tenant.get_multi(db)
    overview = []
    
    for tenant in tenants:
        user_count = len(crud.user.get_users_by_tenant(db, tenant_id=tenant.id))
        overview.append({
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "is_active": tenant.is_active,
            "user_count": user_count,
            "max_users": tenant.max_users,
        })
    
    return {
        "tenants": overview,
        "total_tenants": len(tenants),
        "requested_by": current_user.email,
    }