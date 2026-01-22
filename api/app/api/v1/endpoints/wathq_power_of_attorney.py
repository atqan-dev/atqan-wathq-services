"""
Power of Attorney endpoints for Wathq schema.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_wathq_power_of_attorney import power_of_attorney
from app.schemas.wathq_power_of_attorney import (
    PowerOfAttorney,
    PowerOfAttorneyCreate,
    PowerOfAttorneyUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[PowerOfAttorney])
def read_power_of_attorneys(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Retrieve power of attorney records with all related data.
    """
    poas = power_of_attorney.get_multi_with_relations(db, skip=skip, limit=limit)
    return poas


@router.get("/{id}", response_model=PowerOfAttorney)
def read_power_of_attorney(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get power of attorney by ID with all related data.
    """
    poa = power_of_attorney.get_with_relations(db, id=id)
    if not poa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Power of attorney not found",
        )
    return poa


@router.get("/code/{code}", response_model=PowerOfAttorney)
def read_power_of_attorney_by_code(
    *,
    db: Session = Depends(deps.get_db),
    code: str,
) -> Any:
    """
    Get power of attorney by code with all related data.
    """
    poa = power_of_attorney.get_by_code(db, code=code)
    if not poa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Power of attorney not found",
        )
    return poa


@router.post("/", response_model=PowerOfAttorney, status_code=status.HTTP_201_CREATED)
def create_power_of_attorney(
    *,
    db: Session = Depends(deps.get_db),
    poa_in: PowerOfAttorneyCreate,
) -> Any:
    """
    Create new power of attorney.
    """
    # Check if code already exists
    existing_poa = power_of_attorney.get_by_code(db, code=poa_in.code)
    if existing_poa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Power of attorney with this code already exists",
        )
    
    poa = power_of_attorney.create(db, obj_in=poa_in)
    return poa


@router.put("/{id}", response_model=PowerOfAttorney)
def update_power_of_attorney(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    poa_in: PowerOfAttorneyUpdate,
) -> Any:
    """
    Update power of attorney.
    """
    poa = power_of_attorney.get(db, id=id)
    if not poa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Power of attorney not found",
        )
    
    # If code is being updated, check if new code already exists
    if poa_in.code and poa_in.code != poa.code:
        existing_poa = power_of_attorney.get_by_code(db, code=poa_in.code)
        if existing_poa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Power of attorney with this code already exists",
            )
    
    poa = power_of_attorney.update(db, db_obj=poa, obj_in=poa_in)
    return poa


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_power_of_attorney(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> None:
    """
    Delete power of attorney.
    """
    poa = power_of_attorney.get(db, id=id)
    if not poa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Power of attorney not found",
        )
    power_of_attorney.remove(db, id=id)
