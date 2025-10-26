"""
HTTP client for Wathq Commercial Registration API with call tracking.
"""

import httpx
import uuid
import time
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.wathq_tracker import WathqCallTracker
from app.core.wathq_utils import get_service_id_by_slug
from app.core.wathq_logger import WathqAPILogger, WathqRequestStatus


class WathqClient:
    """HTTP client for Wathq Commercial Registration API with tracking."""
    
    def __init__(self, api_key: str, db: Session, tenant_id: Optional[int] = None, user_id: Optional[int] = None):
        self.base_url = "https://api.wathq.sa/commercial-registration"
        self.api_key = api_key
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.service_slug = "commercial-registration"
        
        if not api_key:
            tenant_info = f" for tenant {tenant_id}" if tenant_id else ""
            raise ValueError(f"No WATHQ API key found{tenant_info} and service {self.service_slug}")
            
        self.headers = {
            "apiKey": api_key,
            "Content-Type": "application/json",
            "accept": "application/json",
            "Cookie": "BIGipServer~INTG~api.wathq.sa_Pool=755767468.20480.0000"
        }
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to Wathq API with tracking."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        with WathqCallTracker.track_call(
            db=self.db,
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            service_slug=self.service_slug,
            endpoint=endpoint,
            method="GET"
        ) as tracker:
            
            tracker.set_request_data({"params": params or {}})
            
            # Log outgoing request
            WathqAPILogger.log_request(
                request_id=request_id,
                service=self.service_slug,
                endpoint=endpoint,
                method="GET",
                user_id=self.user_id,
                tenant_id=self.tenant_id,
                params=params or {},
                headers=self.headers
            )
            
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    url = f"{self.base_url}{endpoint}"
                    response = await client.get(
                        url,
                        headers=self.headers,
                        params=params or {},
                        timeout=30.0
                    )
                    
                    response_data = response.json()
                    response_time_ms = int((time.time() - start_time) * 1000)
                    response_size = len(str(response_data))
                    
                    # Get service ID for offline storage
                    service_id = get_service_id_by_slug(self.db, self.service_slug)
                    full_url = f"{self.base_url}{endpoint}"
                    
                    tracker.log_response(
                        status_code=response.status_code,
                        response_body=response_data,
                        service_id=service_id,
                        full_url=full_url
                    )
                    
                    # Log successful response
                    WathqAPILogger.log_response(
                        request_id=request_id,
                        service=self.service_slug,
                        endpoint=endpoint,
                        status_code=response.status_code,
                        response_time_ms=response_time_ms,
                        response_size_bytes=response_size,
                        status=WathqRequestStatus.SUCCESS,
                        response_body=response_data,
                        user_id=self.user_id,
                        tenant_id=self.tenant_id
                    )
                    
                    response.raise_for_status()
                    return response_data
                    
            except httpx.TimeoutException as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                WathqAPILogger.log_error(
                    request_id=request_id,
                    service=self.service_slug,
                    endpoint=endpoint,
                    error_type="TimeoutException",
                    error_message=str(e),
                    user_id=self.user_id,
                    tenant_id=self.tenant_id
                )
                error_response = {"error": str(e), "type": "TimeoutException"}
                tracker.log_response(504, error_response)
                raise
                
            except httpx.HTTPStatusError as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                status_code = e.response.status_code
                
                # Determine status type
                if status_code == 401:
                    status = WathqRequestStatus.UNAUTHORIZED
                elif status_code >= 500:
                    status = WathqRequestStatus.SERVER_ERROR
                else:
                    status = WathqRequestStatus.FAILED
                
                WathqAPILogger.log_response(
                    request_id=request_id,
                    service=self.service_slug,
                    endpoint=endpoint,
                    status_code=status_code,
                    response_time_ms=response_time_ms,
                    response_size_bytes=len(str(e.response.text)),
                    status=status,
                    error_message=str(e),
                    user_id=self.user_id,
                    tenant_id=self.tenant_id
                )
                error_response = {"error": str(e), "type": "HTTPStatusError"}
                tracker.log_response(status_code, error_response)
                raise
                
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                error_response = {"error": str(e), "type": type(e).__name__}
                status_code = 500
                
                # Try to extract status code from exception
                if hasattr(e, 'response'):
                    response_obj = getattr(e, 'response')
                    if hasattr(response_obj, 'status_code'):
                        status_code = response_obj.status_code
                    elif isinstance(response_obj, dict):
                        status_code = response_obj.get('status_code', 500)
                
                WathqAPILogger.log_error(
                    request_id=request_id,
                    service=self.service_slug,
                    endpoint=endpoint,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    user_id=self.user_id,
                    tenant_id=self.tenant_id
                )
                tracker.log_response(status_code, error_response)
                raise
    
    async def get_full_info(self, cr_id: str, language: str = "ar") -> Dict[str, Any]:
        """Get full commercial registration information."""
        return await self._make_request(f"/fullinfo/{cr_id}", {"language": language})
    
    async def get_basic_info(self, cr_id: str, language: str = "ar") -> Dict[str, Any]:
        """Get basic commercial registration information."""
        return await self._make_request(f"/info/{cr_id}", {"language": language})
    
    async def get_branches(self, cr_id: str, language: str = "ar") -> Dict[str, Any]:
        """Get commercial registration branches."""
        return await self._make_request(f"/branches/{cr_id}", {"language": language})
    
    async def get_status(self, cr_id: str, language: str = "ar") -> Dict[str, Any]:
        """Get commercial registration status."""
        return await self._make_request(f"/status/{cr_id}", {"language": language})
    
    async def get_capital(self, cr_id: str, language: str = "ar") -> Dict[str, Any]:
        """Get commercial registration capital details."""
        return await self._make_request(f"/capital/{cr_id}", {"language": language})
    
    async def get_managers(self, cr_id: str, language: str = "ar") -> Dict[str, Any]:
        """Get commercial registration managers."""
        return await self._make_request(f"/managers/{cr_id}", {"language": language})
    
    async def get_owners(self, cr_id: str, language: str = "ar") -> Dict[str, Any]:
        """Get commercial registration owners."""
        return await self._make_request(f"/owners/{cr_id}", {"language": language})
    
    async def get_related(self, identity_id: str, id_type: str, language: str = "ar") -> Dict[str, Any]:
        """Get related commercial registrations for an identity."""
        return await self._make_request(f"/related/{identity_id}/{id_type}", {"language": language})
    
    async def check_ownership(self, identity_id: str, id_type: str) -> Dict[str, Any]:
        """Check if identity owns a commercial registration."""
        return await self._make_request(f"/owns/{identity_id}/{id_type}")
    
    async def get_cr_national_number(self, cr_number: str) -> Dict[str, Any]:
        """Get commercial registration national number."""
        return await self._make_request(f"/crNationalNumber/{cr_number}")
    
    # Lookup endpoints
    async def get_status_lookup(self) -> Dict[str, Any]:
        """Get all status lookups."""
        return await self._make_request("/lookup/status")
    
    async def get_entity_type_lookup(self) -> Dict[str, Any]:
        """Get all entity type lookups."""
        return await self._make_request("/lookup/entityType")
    
    async def get_company_form_lookup(self) -> Dict[str, Any]:
        """Get all company form lookups."""
        return await self._make_request("/lookup/companyForm")
    
    async def get_company_character_lookup(self) -> Dict[str, Any]:
        """Get all company character lookups."""
        return await self._make_request("/lookup/companyCharacter")
    
    async def get_relation_lookup(self) -> Dict[str, Any]:
        """Get all relation lookups."""
        return await self._make_request("/lookup/relation")
    
    async def get_manager_positions_lookup(self) -> Dict[str, Any]:
        """Get all manager positions lookups."""
        return await self._make_request("/lookup/managerPositions")
    
    async def get_identifier_type_lookup(self) -> Dict[str, Any]:
        """Get all identifier type lookups."""
        return await self._make_request("/lookup/identifierType")
    
    async def get_management_structure_lookup(self) -> Dict[str, Any]:
        """Get all management structure lookups."""
        return await self._make_request("/lookup/managementStructure")
    
    async def get_partner_type_lookup(self) -> Dict[str, Any]:
        """Get all partner type lookups."""
        return await self._make_request("/lookup/partnerType")
    
    async def get_partnership_type_lookup(self) -> Dict[str, Any]:
        """Get all partnership type lookups."""
        return await self._make_request("/lookup/partnershipType")
    
    async def get_nationalities_lookup(self) -> Dict[str, Any]:
        """Get all nationalities lookups."""
        return await self._make_request("/lookup/nationalities")
    
    async def get_activities_lookup(self) -> Dict[str, Any]:
        """Get all activities lookups."""
        return await self._make_request("/lookup/activities")
    
    async def get_cities_lookup(self) -> Dict[str, Any]:
        """Get all cities lookups."""
        return await self._make_request("/lookup/cities")
    
    async def get_currencies_lookup(self) -> Dict[str, Any]:
        """Get all currencies lookups."""
        return await self._make_request("/lookup/currencies")