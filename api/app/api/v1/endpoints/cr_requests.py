from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.CrRequest])
def read_cr_requests(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve CR requests.
    """
    cr_requests = crud.cr_request.get_recent(db, skip=skip, limit=limit)
    return cr_requests


@router.post("/", response_model=schemas.CrRequest)
def create_cr_request(
    *,
    db: Session = Depends(deps.get_db),
    cr_request_in: schemas.CrRequestCreate,
) -> Any:
    """
    Create new CR request.
    """
    cr_request = crud.cr_request.create(db=db, obj_in=cr_request_in)
    return cr_request


@router.get("/{id}", response_model=schemas.CrRequest)
def read_cr_request(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    """
    Get CR request by ID.
    """
    cr_request = crud.cr_request.get(db=db, id=id)
    if not cr_request:
        raise HTTPException(status_code=404, detail="CR request not found")
    return cr_request


@router.put("/{id}", response_model=schemas.CrRequest)
def update_cr_request(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    cr_request_in: schemas.CrRequestUpdate,
) -> Any:
    """
    Update a CR request.
    """
    cr_request = crud.cr_request.get(db=db, id=id)
    if not cr_request:
        raise HTTPException(status_code=404, detail="CR request not found")
    cr_request = crud.cr_request.update(db=db, db_obj=cr_request, obj_in=cr_request_in)
    return cr_request


@router.delete("/{id}", response_model=schemas.CrRequest)
def delete_cr_request(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    """
    Delete a CR request.
    """
    cr_request = crud.cr_request.get(db=db, id=id)
    if not cr_request:
        raise HTTPException(status_code=404, detail="CR request not found")
    cr_request = crud.cr_request.remove(db=db, id=id)
    return cr_request


@router.get("/by-cr-number/{cr_number}", response_model=List[schemas.CrRequest])
def read_cr_requests_by_cr_number(
    *,
    db: Session = Depends(deps.get_db),
    cr_number: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get CR requests by CR number.
    """
    cr_requests = crud.cr_request.get_by_cr_number(
        db, cr_number=cr_number, skip=skip, limit=limit
    )
    return cr_requests


@router.get("/by-status/{status_number}", response_model=List[schemas.CrRequest])
def read_cr_requests_by_status(
    *,
    db: Session = Depends(deps.get_db),
    status_number: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get CR requests by status number.
    """
    cr_requests = crud.cr_request.get_by_status(
        db, status_number=status_number, skip=skip, limit=limit
    )
    return cr_requests
