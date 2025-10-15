"""
FastAPI endpoints for Wathq Employee Information API.
"""

from fastapi import APIRouter, Depends, HTTPException, Path

from app.core.guards import require_management_user
from .client import employee_client
from .schemas import EmployeeInfoResponse

router = APIRouter()


@router.get("/info/{employee_id}", response_model=EmployeeInfoResponse)
async def get_employee_info(
    employee_id: str = Path(..., min_length=10, max_length=10, description="National ID or Iqama number"),
    _: dict = Depends(require_management_user)
):
    """Get employee information by ID."""
    try:
        return await employee_client.get_employee_info(employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))