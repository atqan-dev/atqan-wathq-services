"""
HTTP client for Wathq SPL National Address API.
"""

import httpx
from typing import List

from app.core.config import settings
from .schemas import NationalAddressInfo


class WathqSplNationalAddressClient:
    def __init__(self):
        self.base_url = "https://api.wathq.sa/spl/national/address"
        self.headers = {
            "apiKey": settings.WATHQ_API_KEY,
            "Content-Type": "application/json"
        }

    async def get_address_info(self, cr_number: str) -> List[NationalAddressInfo]:
        """Get national address information by CR number."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/info/{cr_number}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return [NationalAddressInfo(**item) for item in data]


spl_national_address_client = WathqSplNationalAddressClient()