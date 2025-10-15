"""
FastAPI endpoints for Wathq Attorney API.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.guards import require_management_user
from .client import attorney_client
from .schemas import LookupResponse, AttorneyInfoResponse

router = APIRouter()


@router.get("/lookup", response_model=LookupResponse)
async def get_attorney_lookup(
    _: dict = Depends(require_management_user)
):
    """Get attorney texts lookup data."""
    try:
        return await attorney_client.get_lookup()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{code}", response_model=AttorneyInfoResponse)
async def get_attorney_info(
    code: str,
    principal_id: Optional[str] = Query(None, description="Principal ID"),
    agent_id: Optional[str] = Query(None, description="Agent ID"),
    _: dict = Depends(require_management_user)
):
    """Get attorney information by code and ID."""
    if not principal_id and not agent_id:
        raise HTTPException(
            status_code=400, 
            detail="Either principal_id or agent_id is required"
        )
    
    try:
        return await attorney_client.get_attorney_info(code, principal_id, agent_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))