"""
National Addresses endpoints for Wathq schema.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_wathq_national_address import address
from app.schemas.wathq_national_address import (
    Address,
    AddressCreate,
    AddressUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[Address])
def read_addresses(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Retrieve national addresses.
    """
    addresses = address.get_multi(db, skip=skip, limit=limit)
    return addresses


@router.get("/{pk_address_id}", response_model=Address)
def read_address(
    *,
    db: Session = Depends(deps.get_db),
    pk_address_id: str,
) -> Any:
    """
    Get address by ID.
    """
    address_obj = address.get(db, id=pk_address_id)
    if not address_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    return address_obj


@router.get("/post-code/{post_code}", response_model=List[Address])
def read_addresses_by_post_code(
    *,
    db: Session = Depends(deps.get_db),
    post_code: str,
) -> Any:
    """
    Get addresses by post code.
    """
    addresses = address.get_by_post_code(db, post_code=post_code)
    return addresses


@router.get("/city/{city}", response_model=List[Address])
def read_addresses_by_city(
    *,
    db: Session = Depends(deps.get_db),
    city: str,
) -> Any:
    """
    Get addresses by city.
    """
    addresses = address.get_by_city(db, city=city)
    return addresses


@router.get("/region/{region_id}", response_model=List[Address])
def read_addresses_by_region(
    *,
    db: Session = Depends(deps.get_db),
    region_id: str,
) -> Any:
    """
    Get addresses by region ID.
    """
    addresses = address.get_by_region(db, region_id=region_id)
    return addresses


@router.get("/primary/all", response_model=List[Address])
def read_primary_addresses(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Get all primary addresses.
    """
    addresses = address.get_primary_addresses(db, skip=skip, limit=limit)
    return addresses


@router.post("/", response_model=Address, status_code=status.HTTP_201_CREATED)
def create_address(
    *,
    db: Session = Depends(deps.get_db),
    address_in: AddressCreate,
) -> Any:
    """
    Create new address.
    """
    # Check if address with this ID already exists
    existing_address = address.get(db, id=address_in.pk_address_id)
    if existing_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Address with this ID already exists",
        )
    
    address_obj = address.create(db, obj_in=address_in)
    return address_obj


@router.put("/{pk_address_id}", response_model=Address)
def update_address(
    *,
    db: Session = Depends(deps.get_db),
    pk_address_id: str,
    address_in: AddressUpdate,
) -> Any:
    """
    Update address.
    """
    address_obj = address.get(db, id=pk_address_id)
    if not address_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    
    address_obj = address.update(db, db_obj=address_obj, obj_in=address_in)
    return address_obj


@router.delete("/{pk_address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    *,
    db: Session = Depends(deps.get_db),
    pk_address_id: str,
) -> None:
    """
    Delete address.
    """
    address_obj = address.get(db, id=pk_address_id)
    if not address_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    address.remove(db, id=pk_address_id)
