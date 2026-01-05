"""
Commercial Registration endpoints for Wathq schema.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_wathq_commercial_registration import commercial_registration
from app.schemas.wathq_commercial_registration import (
    CommercialRegistration,
    CommercialRegistrationCreate,
    CommercialRegistrationUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[CommercialRegistration])
def get_commercial_registrations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
) -> Any:
    """
    Retrieve commercial registrations with all related data.
    """
    crs = commercial_registration.get_multi_with_relations(db, skip=skip, limit=limit)
    return crs


@router.get("/search", response_model=list[CommercialRegistration])
def search_commercial_registrations(
    name: str = Query(..., min_length=1),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
) -> Any:
    """
    Search commercial registrations by name.
    """
    crs = commercial_registration.search_by_name(db, name=name, skip=skip, limit=limit)
    return crs


@router.get("/by-status/{status_id}", response_model=list[CommercialRegistration])
def get_commercial_registrations_by_status(
    status_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
) -> Any:
    """
    Get commercial registrations by status ID.
    """
    crs = commercial_registration.get_by_status(
        db, status_id=status_id, skip=skip, limit=limit
    )
    return crs


@router.get("/by-city/{city_id}", response_model=list[CommercialRegistration])
def get_commercial_registrations_by_city(
    city_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
) -> Any:
    """
    Get commercial registrations by headquarter city ID.
    """
    crs = commercial_registration.get_by_city(
        db, city_id=city_id, skip=skip, limit=limit
    )
    return crs


@router.get("/{cr_number}", response_model=CommercialRegistration)
def get_commercial_registration(
    cr_number: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get commercial registration by CR number with all related data.
    """
    cr = commercial_registration.get_by_cr_number(db, cr_number=cr_number)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commercial registration not found",
        )
    return cr


@router.post("/", response_model=CommercialRegistration, status_code=status.HTTP_201_CREATED)
def create_commercial_registration(
    *,
    db: Session = Depends(deps.get_db),
    cr_in: CommercialRegistrationCreate,
) -> Any:
    """
    Create new commercial registration.
    """
    existing_cr = commercial_registration.get_by_cr_number(db, cr_number=cr_in.cr_number)
    if existing_cr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Commercial registration with this CR number already exists",
        )
    
    cr = commercial_registration.create(db, obj_in=cr_in)
    return cr


@router.put("/{cr_number}", response_model=CommercialRegistration)
def update_commercial_registration(
    *,
    db: Session = Depends(deps.get_db),
    cr_number: str,
    cr_in: CommercialRegistrationUpdate,
) -> Any:
    """
    Update commercial registration.
    """
    cr = commercial_registration.get_by_cr_number(db, cr_number=cr_number)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commercial registration not found",
        )
    
    cr = commercial_registration.update(db, db_obj=cr, obj_in=cr_in)
    return cr


@router.delete("/{cr_number}")
def delete_commercial_registration(
    cr_number: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Delete commercial registration.
    """
    cr = commercial_registration.get_by_cr_number(db, cr_number=cr_number)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commercial registration not found",
        )
    
    db.delete(cr)
    db.commit()
    return {"message": "Commercial registration deleted successfully"}
