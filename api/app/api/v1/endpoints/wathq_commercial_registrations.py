"""
Commercial Registration endpoints for Wathq schema.
"""

from typing import Any, Dict

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


@router.get("/")
def get_commercial_registrations(
    db: Session = Depends(deps.get_db),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=1000),
    search: str = Query(default=""),
    sort_by: str = Query(default="cr_number"),
    sort_order: str = Query(default="asc"),
    status_name: str = Query(default=""),
    headquarter_city_name: str = Query(default=""),
    cr_number: str = Query(default=""),
) -> Dict[str, Any]:
    """
    Retrieve commercial registrations with all related data.
    Supports pagination, search, and filtering.
    Returns paginated response with total count.
    """
    from app.models.wathq_commercial_registration import CommercialRegistration as CRModel
    from sqlalchemy import or_, and_, desc, asc
    
    # Build query with filters
    query = db.query(CRModel)
    
    # Apply filters
    filters = []
    
    if status_name and status_name.lower() != "all statuses":
        filters.append(CRModel.status_name == status_name)
    
    if headquarter_city_name and headquarter_city_name.lower() != "all cities":
        filters.append(CRModel.headquarter_city_name == headquarter_city_name)
    
    if cr_number:
        filters.append(CRModel.cr_number.like(f"%{cr_number}%"))
    
    if search:
        search_filter = or_(
            CRModel.cr_number.like(f"%{search}%"),
            CRModel.name.like(f"%{search}%"),
            CRModel.headquarter_city_name.like(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Get total count with filters
    total = query.count()
    
    # Apply sorting
    if sort_by and hasattr(CRModel, sort_by):
        sort_column = getattr(CRModel, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
    
    # Apply pagination
    skip = (page - 1) * limit
    crs = query.offset(skip).limit(limit).all()
    
    # Convert to Pydantic models for proper serialization
    data = [CommercialRegistration.model_validate(cr) for cr in crs]
    
    return {
        "data": data,
        "total": total,
        "page": page,
        "pageSize": limit,
        "totalPages": (total + limit - 1) // limit  # Ceiling division
    }


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


@router.get("/{id}", response_model=CommercialRegistration)
def get_commercial_registration(
    id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get commercial registration by ID with all related data.
    """
    cr = commercial_registration.get_with_relations(db, id=id)
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
    Allow duplicate CR numbers since users can request the same CR multiple times.
    Each request is uniquely identified by its auto-generated ID.
    """
    cr = commercial_registration.create(db, obj_in=cr_in)
    return cr


@router.put("/{id}", response_model=CommercialRegistration)
def update_commercial_registration(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    cr_in: CommercialRegistrationUpdate,
) -> Any:
    """
    Update commercial registration.
    """
    cr = commercial_registration.get(db, id=id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commercial registration not found",
        )
    
    cr = commercial_registration.update(db, db_obj=cr, obj_in=cr_in)
    return cr


@router.delete("/{id}")
def delete_commercial_registration(
    id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Delete commercial registration.
    """
    cr = commercial_registration.get(db, id=id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commercial registration not found",
        )
    
    db.delete(cr)
    db.commit()
    return {"message": "Commercial registration deleted successfully"}
