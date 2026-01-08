"""
Corporate Contract endpoints for Wathq schema.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_wathq_corporate_contract import corporate_contract
from app.schemas.wathq_corporate_contract import (
    CorporateContract,
    CorporateContractCreate,
    CorporateContractUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[CorporateContract])
def read_corporate_contracts(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Retrieve corporate contracts with all related data.
    """
    contracts = corporate_contract.get_multi_with_relations(db, skip=skip, limit=limit)
    return contracts


@router.get("/{id}", response_model=CorporateContract)
def read_corporate_contract(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get corporate contract by ID with all related data.
    """
    contract = corporate_contract.get_with_relations(db, id=id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corporate contract not found",
        )
    return contract


@router.post("/", response_model=CorporateContract, status_code=status.HTTP_201_CREATED)
def create_corporate_contract(
    *,
    db: Session = Depends(deps.get_db),
    contract_in: CorporateContractCreate,
) -> Any:
    """
    Create new corporate contract.
    """
    contract = corporate_contract.create(db, obj_in=contract_in)
    return contract


@router.put("/{id}", response_model=CorporateContract)
def update_corporate_contract(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    contract_in: CorporateContractUpdate,
) -> Any:
    """
    Update corporate contract.
    """
    contract = corporate_contract.get(db, id=id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corporate contract not found",
        )
    contract = corporate_contract.update(db, db_obj=contract, obj_in=contract_in)
    return contract


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_corporate_contract(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> None:
    """
    Delete corporate contract.
    """
    contract = corporate_contract.get(db, id=id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corporate contract not found",
        )
    corporate_contract.remove(db, id=id)
