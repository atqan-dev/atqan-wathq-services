"""
HTTP client for Wathq Attorney API.
"""

import httpx
from typing import Optional

from app.core.config import settings
from .schemas import LookupResponse, AttorneyInfoResponse


class WathqAttorneyClient:
    def __init__(self):
        self.base_url = "https://api.wathq.sa/v1/attorney"
        self.headers = {
            "apiKey": settings.WATHQ_API_KEY,
            "Content-Type": "application/json"
        }

    async def get_lookup(self) -> LookupResponse:
        """Get attorney texts lookup data."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/lookup",
                headers=self.headers
            )
            response.raise_for_status()
            return LookupResponse(**response.json())

    async def get_attorney_info(
        self, 
        code: str, 
        principal_id: Optional[str] = None, 
        agent_id: Optional[str] = None
    ) -> AttorneyInfoResponse:
        """Get attorney information by code and ID."""
        params = {}
        if principal_id:
            params["principalId"] = principal_id
        if agent_id:
            params["agentId"] = agent_id
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/info/{code}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return AttorneyInfoResponse(**response.json())


attorney_client = WathqAttorneyClient()