"""
FastAPI endpoints for Wathq Company Contract API.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.core.guards import require_management_user
from app.wathq.company_contract.client import WathqCompanyContractClient
from app.wathq.company_contract import schemas
from app.core.config import settings

router = APIRouter()


def get_wathq_company_contract_client() -> WathqCompanyContractClient:
    """Get Wathq Company Contract client instance."""
    return WathqCompanyContractClient(settings.WATHQ_API_KEY)


@router.get("/info/{cr_national_number}", response_model=schemas.CompanyContractInfo)
async def get_contract_info(
    cr_national_number: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    copy_number: Optional[str] = Query(None),
    current_user = Depends(require_management_user()),
    client: WathqCompanyContractClient = Depends(get_wathq_company_contract_client)
) -> Any:
    """
    Retrieve all company contract info, basic partners, and managers info.
    
    - **cr_national_number**: Commercial Registration National Number
    - **language**: Contract information language (ar/en)
    - **copy_number**: Contract copy number (optional)
    """
    try:
        result = await client.get_contract_info(cr_national_number, language, copy_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/management/{cr_national_number}", response_model=schemas.ManagementResponse)
async def get_management_info(
    cr_national_number: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    current_user = Depends(require_management_user()),
    client: WathqCompanyContractClient = Depends(get_wathq_company_contract_client)
) -> Any:
    """
    Retrieve all management information.
    
    - **cr_national_number**: Commercial Registration National Number
    - **language**: Contract information language (ar/en)
    """
    try:
        result = await client.get_management_info(cr_national_number, language)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/manager/{cr_national_number}/{manager_id}/{id_type}", response_model=schemas.ManagerResponse)
async def get_manager_info(
    cr_national_number: str,
    manager_id: str,
    id_type: str,
    permission_id: Optional[str] = Query(None, min_length=3, max_length=4),
    language: str = Query("ar", regex="^(ar|en)$"),
    current_user = Depends(require_management_user()),
    client: WathqCompanyContractClient = Depends(get_wathq_company_contract_client)
) -> Any:
    """
    Retrieve manager info with permissions.
    
    - **cr_national_number**: Commercial Registration National Number
    - **manager_id**: Manager identification number
    - **id_type**: Identification type (National_ID, Resident_ID, etc.)
    - **permission_id**: Permission role id (optional)
    - **language**: Contract information language (ar/en)
    """
    # Validate id_type
    valid_id_types = [
        "National_ID", "Resident_ID", "Passport", "GCC_ID", "Endowment_Deed_No",
        "License_No", "CR_National_ID", "Foreign_CR_No", "National_Number",
        "Boarder_Number", "CR_Number", "UndefinedD"
    ]
    
    if id_type not in valid_id_types:
        raise HTTPException(status_code=400, detail="Invalid ID type")
    
    try:
        result = await client.get_manager_info(
            cr_national_number, manager_id, id_type, permission_id, language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Lookup endpoints
@router.get("/lookup/articleParts", response_model=List[schemas.Lookup])
async def get_article_parts_lookup(
    current_user = Depends(require_management_user()),
    client: WathqCompanyContractClient = Depends(get_wathq_company_contract_client)
) -> Any:
    """Retrieve all article parts lookups."""
    try:
        result = await client.get_article_parts_lookup()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/lookup/partnerDecision", response_model=List[schemas.Lookup])
async def get_partner_decision_lookup(
    current_user = Depends(require_management_user()),
    client: WathqCompanyContractClient = Depends(get_wathq_company_contract_client)
) -> Any:
    """Retrieve all partner decision lookups."""
    try:
        result = await client.get_partner_decision_lookup()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/lookup/exerciseMethod", response_model=List[schemas.Lookup])
async def get_exercise_method_lookup(
    current_user = Depends(require_management_user()),
    client: WathqCompanyContractClient = Depends(get_wathq_company_contract_client)
) -> Any:
    """Retrieve all exercise method lookups."""
    try:
        result = await client.get_exercise_method_lookup()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))