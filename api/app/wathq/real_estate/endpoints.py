"""
FastAPI endpoints for Wathq Real Estate API.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.wathq_utils import get_tenant_wathq_key_by_slug
from app.models import User
from .client import WathqRealEstateClient
from .schemas import DeedResponse, IdType

router = APIRouter()


def get_wathq_client(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> WathqRealEstateClient:
    """Get Wathq real estate client instance with tenant-specific API key."""
    api_key = get_tenant_wathq_key_by_slug(
        db=db,
        tenant_id=current_user.tenant_id,
        service_slug="real-estate"
    )
    
    return WathqRealEstateClient(
        api_key=api_key,
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


@router.get("/deed/{deed_number}/{id_number}/{id_type}", response_model=DeedResponse)
async def get_deed_details(
    deed_number: int,
    id_number: str,
    id_type: IdType,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    client: WathqRealEstateClient = Depends(get_wathq_client)
):
    """Get real estate deed details."""
    try:
        return await client.get_deed_details(deed_number, id_number, id_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))