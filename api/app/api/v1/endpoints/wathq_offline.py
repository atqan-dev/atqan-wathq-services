"""
WATHQ offline data API endpoints.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# Routes are ordered from most specific to least specific
# This ensures that specific paths like /my-data and /search match before the generic /{data_id}

@router.get("/my-data", response_model=List[schemas.WathqOfflineData])
def get_my_offline_data(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User | models.ManagementUser = Depends(deps.get_current_active_user_or_management),
) -> Any:
    """
    Get offline WATHQ data for current user.
    Works for both tenant users and management users.
    """
    # Check if it's a management user
    if isinstance(current_user, models.ManagementUser):
        # Get data fetched by this management user
        offline_data = db.query(models.WathqOfflineData).filter(
            models.WathqOfflineData.management_user_id == current_user.id
        ).order_by(models.WathqOfflineData.fetched_at.desc()).offset(skip).limit(limit).all()
    else:
        # Get data fetched by this tenant user
        offline_data = crud.wathq_offline_data.get_by_tenant(
            db=db, tenant_id=current_user.tenant_id, skip=skip, limit=limit
        )
    return offline_data


@router.get("/search", response_model=List[schemas.WathqOfflineData])
def search_offline_data(
    url_pattern: str = Query(..., description="URL pattern to search for"),
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User | models.ManagementUser = Depends(deps.get_current_active_user_or_management),
) -> Any:
    """
    Search offline WATHQ data by URL pattern.
    Works for both tenant users and management users.
    """
    # Check if it's a management user
    if isinstance(current_user, models.ManagementUser):
        # Search data fetched by this management user
        offline_data = db.query(models.WathqOfflineData).filter(
            models.WathqOfflineData.management_user_id == current_user.id,
            models.WathqOfflineData.full_external_url.ilike(f"%{url_pattern}%")
        ).order_by(models.WathqOfflineData.fetched_at.desc()).offset(skip).limit(limit).all()
    else:
        # Search data for tenant user
        offline_data = crud.wathq_offline_data.search_by_url_pattern(
            db=db,
            tenant_id=current_user.tenant_id,
            url_pattern=url_pattern,
            skip=skip,
            limit=limit
        )
    return offline_data


@router.get("/service/{service_identifier}", response_model=List[schemas.WathqOfflineData])
def get_offline_data_by_service(
    service_identifier: str,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User | models.ManagementUser = Depends(deps.get_current_active_user_or_management),
) -> Any:
    """
    Get offline WATHQ data for specific service.
    service_identifier can be either a UUID or a service slug (e.g., 'commercial-registration').
    Works for both tenant users and management users.
    """
    from fastapi import HTTPException

    # Try to parse as UUID first, otherwise treat as slug
    service_id = None
    try:
        service_id = UUID(service_identifier)
    except ValueError:
        # Not a UUID, try to find by slug
        service = db.query(models.Service).filter(
            models.Service.slug == service_identifier
        ).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        service_id = service.id

    # Check if it's a management user
    if isinstance(current_user, models.ManagementUser):
        # Get data fetched by this management user for the service
        offline_data = db.query(models.WathqOfflineData).filter(
            models.WathqOfflineData.management_user_id == current_user.id,
            models.WathqOfflineData.service_id == service_id
        ).order_by(models.WathqOfflineData.fetched_at.desc()).offset(skip).limit(limit).all()
    else:
        # Get data for tenant user
        offline_data = crud.wathq_offline_data.get_by_service_and_tenant(
            db=db,
            service_id=service_id,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit
        )
    return offline_data


@router.get(
    "/service-slug/{service_slug}", response_model=List[schemas.WathqOfflineData]
)
def get_offline_data_by_service_slug(
    service_slug: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(deps.get_current_active_user_or_management),
) -> Any:
    """
    Get specific offline WATHQ data by ID.
    Works for both tenant users and management users.
    """
    from fastapi import HTTPException

    # Check if it's a management user
    if isinstance(current_user, models.ManagementUser):
        # Get data fetched by this management user
        offline_data = db.query(models.WathqOfflineData).filter(
            models.WathqOfflineData.id == data_id,
            models.WathqOfflineData.management_user_id == current_user.id
        ).first()
    else:
        # Get data for tenant user
        offline_data = db.query(models.WathqOfflineData).filter(
            models.WathqOfflineData.id == data_id,
            models.WathqOfflineData.tenant_id == current_user.tenant_id
        ).first()

    if not offline_data:
        raise HTTPException(status_code=404, detail="Offline data not found")

    return offline_data
