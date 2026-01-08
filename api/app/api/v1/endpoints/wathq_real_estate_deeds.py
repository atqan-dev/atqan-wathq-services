"""
Real Estate Deeds endpoints for Wathq schema.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_wathq_real_estate_deed import deed
from app.schemas.wathq_real_estate_deed import (
    Deed,
    DeedCreate,
    DeedUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[Deed])
def read_deeds(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Retrieve real estate deeds with all related data.
    """
    deeds = deed.get_multi_with_relations(db, skip=skip, limit=limit)
    return deeds


@router.get("/{id}", response_model=Deed)
def read_deed(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get deed by ID with all related data.
    """
    deed_obj = deed.get_with_relations(db, id=id)
    if not deed_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deed not found",
        )
    return deed_obj


@router.get("/number/{deed_number}", response_model=Deed)
def read_deed_by_number(
    *,
    db: Session = Depends(deps.get_db),
    deed_number: str,
) -> Any:
    """
    Get deed by deed number with all related data.
    """
    deed_obj = deed.get_by_deed_number(db, deed_number=deed_number)
    if not deed_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deed not found",
        )
    return deed_obj


@router.get("/serial/{deed_serial}", response_model=Deed)
def read_deed_by_serial(
    *,
    db: Session = Depends(deps.get_db),
    deed_serial: str,
) -> Any:
    """
    Get deed by deed serial with all related data.
    """
    deed_obj = deed.get_by_deed_serial(db, deed_serial=deed_serial)
    if not deed_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deed not found",
        )
    return deed_obj


@router.post("/", response_model=Deed, status_code=status.HTTP_201_CREATED)
def create_deed(
    *,
    db: Session = Depends(deps.get_db),
    deed_in: DeedCreate,
) -> Any:
    """
    Create new deed.
    """
    deed_obj = deed.create(db, obj_in=deed_in)
    return deed_obj


@router.put("/{id}", response_model=Deed)
def update_deed(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    deed_in: DeedUpdate,
) -> Any:
    """
    Update deed.
    """
    deed_obj = deed.get(db, id=id)
    if not deed_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deed not found",
        )
    
    deed_obj = deed.update(db, db_obj=deed_obj, obj_in=deed_in)
    return deed_obj


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deed(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> None:
    """
    Delete deed.
    """
    deed_obj = deed.get(db, id=id)
    if not deed_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deed not found",
        )
    deed.remove(db, id=id)
