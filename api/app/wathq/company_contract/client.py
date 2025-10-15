"""
HTTP client for Wathq Company Contract API.
"""

import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


class WathqCompanyContractClient:
    """HTTP client for Wathq Company Contract API."""
    
    def __init__(self, api_key: str):
        self.base_url = "https://api.wathq.sa/company-contract"
        self.api_key = api_key
        self.headers = {
            "apiKey": api_key,
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to Wathq API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params or {},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_contract_info(
        self, 
        cr_national_number: str, 
        language: str = "ar", 
        copy_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get company contract information."""
        params = {"language": language}
        if copy_number:
            params["copyNumber"] = copy_number
        return await self._make_request(f"/info/{cr_national_number}", params)
    
    async def get_management_info(
        self, 
        cr_national_number: str, 
        language: str = "ar"
    ) -> Dict[str, Any]:
        """Get management information."""
        return await self._make_request(f"/management/{cr_national_number}", {"language": language})
    
    async def get_manager_info(
        self, 
        cr_national_number: str, 
        manager_id: str, 
        id_type: str,
        permission_id: Optional[str] = None,
        language: str = "ar"
    ) -> Dict[str, Any]:
        """Get manager information with permissions."""
        params = {"language": language}
        if permission_id:
            params["permissionId"] = permission_id
        return await self._make_request(f"/manager/{cr_national_number}/{manager_id}/{id_type}", params)
    
    # Lookup endpoints
    async def get_article_parts_lookup(self) -> Dict[str, Any]:
        """Get all article parts lookups."""
        return await self._make_request("/lookup/articleParts")
    
    async def get_partner_decision_lookup(self) -> Dict[str, Any]:
        """Get all partner decision lookups."""
        return await self._make_request("/lookup/partnerDecision")
    
    async def get_exercise_method_lookup(self) -> Dict[str, Any]:
        """Get all exercise method lookups."""
        return await self._make_request("/lookup/exerciseMethod")