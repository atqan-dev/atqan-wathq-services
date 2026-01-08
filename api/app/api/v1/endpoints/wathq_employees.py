"""
Employees endpoints for Wathq schema.
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_wathq_employee import employee
from app.schemas.wathq_employee import (
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[Employee])
def read_employees(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Retrieve employees with all related employment details.
    """
    employees = employee.get_multi_with_relations(db, skip=skip, limit=limit)
    return employees


@router.get("/{employee_id}", response_model=Employee)
def read_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_id: int,
) -> Any:
    """
    Get employee by ID with all related employment details.
    """
    employee_obj = employee.get_with_relations(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return employee_obj


@router.get("/nationality/{nationality}", response_model=List[Employee])
def read_employees_by_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality: str,
) -> Any:
    """
    Get employees by nationality.
    """
    employees = employee.get_by_nationality(db, nationality=nationality)
    return employees


@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_in: EmployeeCreate,
) -> Any:
    """
    Create new employee.
    """
    employee_obj = employee.create(db, obj_in=employee_in)
    return employee_obj


@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_id: int,
    employee_in: EmployeeUpdate,
) -> Any:
    """
    Update employee.
    """
    employee_obj = employee.get(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    
    employee_obj = employee.update(db, db_obj=employee_obj, obj_in=employee_in)
    return employee_obj


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_id: int,
) -> None:
    """
    Delete employee.
    """
    employee_obj = employee.get(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    employee.remove(db, id=employee_id)
