"""
FastAPI endpoints for Wathq SPL National Address API.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.core.guards import require_management_user
from .client import spl_national_address_client
from .schemas import NationalAddressInfo

router = APIRouter()


@router.get("/info/{cr_number}", response_model=List[NationalAddressInfo])
async def get_national_address_info(
    cr_number: str,
    _: dict = Depends(require_management_user)
):
    """Get national address information by CR number."""
    try:
        return await spl_national_address_client.get_address_info(cr_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))