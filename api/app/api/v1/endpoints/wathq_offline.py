"""
WATHQ offline data API endpoints.
"""

from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/my-data", response_model=List[schemas.WathqOfflineData])
def get_my_offline_data(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get offline WATHQ data for current user's tenant.
    """
    offline_data = crud.wathq_offline_data.get_by_tenant(
        db=db, tenant_id=current_user.tenant_id, skip=skip, limit=limit
    )
    return offline_data


@router.get("/service/{service_id}", response_model=List[schemas.WathqOfflineData])
def get_offline_data_by_service(
    service_id: UUID,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get offline WATHQ data for specific service within current tenant.
    """
    offline_data = crud.wathq_offline_data.get_by_service_and_tenant(
        db=db, 
        service_id=service_id,
        tenant_id=current_user.tenant_id,
        skip=skip, 
        limit=limit
    )
    return offline_data


@router.get("/search", response_model=List[schemas.WathqOfflineData])
def search_offline_data(
    url_pattern: str = Query(..., description="URL pattern to search for"),
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search offline WATHQ data by URL pattern within current tenant.
    """
    offline_data = crud.wathq_offline_data.search_by_url_pattern(
        db=db,
        tenant_id=current_user.tenant_id,
        url_pattern=url_pattern,
        skip=skip,
        limit=limit
    )
    return offline_data


@router.get("/{data_id}", response_model=schemas.WathqOfflineData)
def get_offline_data_by_id(
    data_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specific offline WATHQ data by ID (tenant-isolated).
    """
    offline_data = db.query(models.WathqOfflineData).filter(
        models.WathqOfflineData.id == data_id,
        models.WathqOfflineData.tenant_id == current_user.tenant_id
    ).first()
    
    if not offline_data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Offline data not found")
    
    return offline_data