from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.CsRequest])
def read_cs_requests(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve CS requests.
    """
    cs_requests = crud.cs_request.get_recent(db, skip=skip, limit=limit)
    return cs_requests


@router.post("/", response_model=schemas.CsRequest)
def create_cs_request(
    *,
    db: Session = Depends(deps.get_db),
    cs_request_in: schemas.CsRequestCreate,
) -> Any:
    """
    Create new CS request.
    """
    cs_request = crud.cs_request.create(db=db, obj_in=cs_request_in)
    return cs_request


@router.get("/{id}", response_model=schemas.CsRequest)
def read_cs_request(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    """
    Get CS request by ID.
    """
    cs_request = crud.cs_request.get(db=db, id=id)
    if not cs_request:
        raise HTTPException(status_code=404, detail="CS request not found")
    return cs_request


@router.put("/{id}", response_model=schemas.CsRequest)
def update_cs_request(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    cs_request_in: schemas.CsRequestUpdate,
) -> Any:
    """
    Update a CS request.
    """
    cs_request = crud.cs_request.get(db=db, id=id)
    if not cs_request:
        raise HTTPException(status_code=404, detail="CS request not found")
    cs_request = crud.cs_request.update(db=db, db_obj=cs_request, obj_in=cs_request_in)
    return cs_request


@router.delete("/{id}", response_model=schemas.CsRequest)
def delete_cs_request(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
) -> Any:
    """
    Delete a CS request.
    """
    cs_request = crud.cs_request.get(db=db, id=id)
    if not cs_request:
        raise HTTPException(status_code=404, detail="CS request not found")
    cs_request = crud.cs_request.remove(db=db, id=id)
    return cs_request


@router.get("/by-cr-number/{cr_number}", response_model=List[schemas.CsRequest])
def read_cs_requests_by_cr_number(
    *,
    db: Session = Depends(deps.get_db),
    cr_number: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get CS requests by CR number.
    """
    cs_requests = crud.cs_request.get_by_cr_number(
        db, cr_number=cr_number, skip=skip, limit=limit
    )
    return cs_requests


@router.get("/by-status/{status_number}", response_model=List[schemas.CsRequest])
def read_cs_requests_by_status(
    *,
    db: Session = Depends(deps.get_db),
    status_number: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get CS requests by status number.
    """
    cs_requests = crud.cs_request.get_by_status(
        db, status_number=status_number, skip=skip, limit=limit
    )
    return cs_requests
