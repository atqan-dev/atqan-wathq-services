"""
FastAPI endpoints for Wathq Commercial Registration API.
"""

from typing import Any, List
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.api.management_deps import get_current_active_management_user
from app.core.config import settings
from app.core.wathq_utils import get_tenant_wathq_key_by_slug
from app.models import User
from app.models.management_user import ManagementUser
from app.wathq.commercial_registration.client import WathqClient
from app.wathq.commercial_registration import schemas

router = APIRouter()

def get_wathq_client_for_tenant_user(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> WathqClient:
    """Get Wathq client instance with tenant-specific API key for tenant users."""
    api_key = get_tenant_wathq_key_by_slug(
        db=db,
        tenant_id=current_user.tenant_id,
        service_slug="commercial-registration"
    )
    
    # Fallback to system API key if tenant doesn't have a specific key
    if not api_key:
        api_key = settings.WATHQ_API_KEY
    
    return WathqClient(
        api_key=api_key,
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )

def get_wathq_client_for_management_user(
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user)
) -> WathqClient:
    """Get Wathq client instance with global API key for management users."""
    return WathqClient(
        api_key=settings.WATHQ_API_KEY,
        db=db,
        tenant_id=None,  # No tenant for management users
        user_id=None  # No user_id for management users
    )




@router.get("/fullinfo/{cr_id}", response_model=schemas.FullInfo)
async def get_full_info(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve all commercial registration data (tenant users)."""
    try:
        client = get_wathq_client_for_tenant_user(db=db, current_user=current_user)
        result = await client.get_full_info(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        # Check if it's an authentication error
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/management/fullinfo/{cr_id}", response_model=schemas.FullInfo)
async def get_full_info_management(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user)
) -> Any:
    """Retrieve all commercial registration data (management users)."""
    try:
        client = get_wathq_client_for_management_user(db=db, current_user=current_user)
        result = await client.get_full_info(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        # Check if it's an authentication error
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/info/{cr_id}", response_model=schemas.BasicInfo)
async def get_basic_info(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve basic commercial registration data (tenant users)."""
    try:
        client = get_wathq_client_for_tenant_user(db=db, current_user=current_user)
        result = await client.get_basic_info(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        # Check if it's an authentication error
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/management/info/{cr_id}", response_model=schemas.BasicInfo)
async def get_basic_info_management(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user)
) -> Any:
    """Retrieve basic commercial registration data (management users)."""
    try:
        client = get_wathq_client_for_management_user(db=db, current_user=current_user)
        result = await client.get_basic_info(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        # Check if it's an authentication error
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/branches/{cr_id}", response_model=List[schemas.Branch])
async def get_branches(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve all commercial registration branches (tenant users)."""
    try:
        client = get_wathq_client_for_tenant_user(db=db, current_user=current_user)
        result = await client.get_branches(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/management/branches/{cr_id}", response_model=List[schemas.Branch])
async def get_branches_management(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user)
) -> Any:
    """Retrieve all commercial registration branches (management users)."""
    try:
        client = get_wathq_client_for_management_user(db=db, current_user=current_user)
        result = await client.get_branches(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/status/{cr_id}", response_model=schemas.Status)
async def get_status(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve status of a commercial registration (tenant users)."""
    try:
        client = get_wathq_client_for_tenant_user(db=db, current_user=current_user)
        result = await client.get_status(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/capital/{cr_id}", response_model=schemas.Capital)
async def get_capital(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve capital details for commercial registration (tenant users)."""
    try:
        client = get_wathq_client_for_tenant_user(db=db, current_user=current_user)
        result = await client.get_capital(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/managers/{cr_id}", response_model=List[schemas.Manager])
async def get_managers(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve a list of managers and board of directors (tenant users)."""
    try:
        client = get_wathq_client_for_tenant_user(db=db, current_user=current_user)
        result = await client.get_managers(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/owners/{cr_id}", response_model=List[schemas.Owner])
async def get_owners(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve the owner of establishment and list of partners (tenant users)."""
    try:
        client = get_wathq_client_for_tenant_user(db=db, current_user=current_user)
        result = await client.get_owners(cr_id, language)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/related/{identity_id}/{id_type}", response_model=schemas.Related)
async def get_related(
    identity_id: str,
    id_type: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    nationality: int = Query(None, description="Nationality NIC code - required for Passport, Foreign_CR_No"),
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve list of commercial registrations with their relation for a given ID.
    
    Parameters:
    - identity_id: Identification number (رقم هوية)
    - id_type: Identification type (National_ID, Resident_ID, Passport, GCC_ID, Endowment_Deed_No, License_No, CR_National_ID, Foreign_CR_No, National_Number, Boarder_Number)
    - language: ar or en
    - nationality: Nationality NIC code (required for certain ID types like Passport, Foreign_CR_No)
    """
    try:
        result = await client.get_related(identity_id, id_type, language, nationality)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/owns/{identity_id}/{id_type}", response_model=schemas.Owns)
async def check_ownership(
    identity_id: str,
    id_type: str,
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Check if given ID is an owner or partner."""
    try:
        result = await client.check_ownership(identity_id, id_type)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/crNationalNumber/{cr_number}", response_model=schemas.CRNationalNumber)
async def get_cr_national_number(
    cr_number: str,
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve commercial registration national number."""
    try:
        result = await client.get_cr_national_number(cr_number)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


# Lookup endpoints
@router.get("/lookup/status", response_model=List[schemas.Lookup])
async def get_status_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all status lookups."""
    try:
        result = await client.get_status_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/entityType", response_model=List[schemas.Lookup])
async def get_entity_type_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all entity type lookups."""
    try:
        result = await client.get_entity_type_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/companyForm", response_model=List[schemas.Lookup])
async def get_company_form_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all company form lookups."""
    try:
        result = await client.get_company_form_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/companyCharacter", response_model=List[schemas.Lookup])
async def get_company_character_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all company character lookups."""
    try:
        result = await client.get_company_character_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/relation", response_model=List[schemas.Lookup])
async def get_relation_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all commercial registration relation lookups."""
    try:
        result = await client.get_relation_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/managerPositions", response_model=List[schemas.Lookup])
async def get_manager_positions_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all manager positions lookups."""
    try:
        result = await client.get_manager_positions_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/identifierType", response_model=List[schemas.Lookup])
async def get_identifier_type_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all identifier type lookups."""
    try:
        result = await client.get_identifier_type_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/managementStructure", response_model=List[schemas.Lookup])
async def get_management_structure_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all management structure lookups."""
    try:
        result = await client.get_management_structure_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/partnerType", response_model=List[schemas.Lookup])
async def get_partner_type_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all partner type lookups."""
    try:
        result = await client.get_partner_type_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/partnershipType", response_model=List[schemas.Lookup])
async def get_partnership_type_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all partnership type lookups."""
    try:
        result = await client.get_partnership_type_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/nationalities")
async def get_nationalities_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all nationalities lookups."""
    try:
        result = await client.get_nationalities_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/activities")
async def get_activities_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all activities lookups."""
    try:
        result = await client.get_activities_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/cities")
async def get_cities_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all cities lookups."""
    try:
        result = await client.get_cities_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.get("/lookup/currencies", response_model=List[schemas.Lookup])
async def get_currencies_lookup(
    client: WathqClient = Depends(get_wathq_client_for_management_user)
) -> Any:
    """Retrieve all currencies lookups."""
    try:
        result = await client.get_currencies_lookup()
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WATHQ API authentication failed. Please verify your API key is valid and has the required permissions."
            )
        raise HTTPException(status_code=400, detail=error_msg)