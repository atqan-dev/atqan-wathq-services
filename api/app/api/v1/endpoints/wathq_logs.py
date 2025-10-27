"""
WATHQ call logs API endpoints.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.permissions import require_permission

router = APIRouter()


@router.get("/my-calls", response_model=List[schemas.WathqCallLog])
def get_my_calls(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User | models.ManagementUser = Depends(deps.get_current_active_user_or_management),
) -> Any:
    """
    Get current user's WATHQ API calls.
    Works for both tenant users and management users.
    """
    # Check if it's a management user
    if isinstance(current_user, models.ManagementUser):
        # Get calls made by this management user
        calls = db.query(models.WathqCallLog).filter(
            models.WathqCallLog.management_user_id == current_user.id
        ).order_by(models.WathqCallLog.fetched_at.desc()).offset(skip).limit(limit).all()
    else:
        # Get calls made by this tenant user
        calls = crud.wathq_call_log.get_by_user(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return calls


@router.get("/tenant-calls", response_model=List[schemas.WathqCallLog])
def get_tenant_calls(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all WATHQ API calls for current user's tenant.
    """
    require_permission(current_user, "view_service_usage")
    
    calls = crud.wathq_call_log.get_by_tenant(
        db=db, tenant_id=current_user.tenant_id, skip=skip, limit=limit
    )
    return calls


@router.get("/service-calls/{service_slug}", response_model=List[schemas.WathqCallLog])
def get_service_calls(
    service_slug: str,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get WATHQ API calls for a specific service within current tenant.
    """
    require_permission(current_user, "view_service_usage")
    
    calls = crud.wathq_call_log.get_by_service(
        db=db, 
        service_slug=service_slug, 
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return calls


@router.get("/stats/tenant", response_model=dict)
def get_tenant_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get WATHQ usage statistics for current tenant.
    """
    require_permission(current_user, "view_service_usage")
    
    total_calls = crud.wathq_call_log.count_calls_by_tenant(
        db=db, tenant_id=current_user.tenant_id
    )
    
    # Get calls by service
    services = ["commercial-registration", "real-estate", "employee-verification", 
               "company-contract", "attorney-services", "national-address"]
    
    service_stats = {}
    for service in services:
        count = crud.wathq_call_log.count_calls_by_service(
            db=db, service_slug=service, tenant_id=current_user.tenant_id
        )
        service_stats[service] = count
    
    return {
        "tenant_id": current_user.tenant_id,
        "total_calls": total_calls,
        "service_breakdown": service_stats
    }