"""
HTTP client for Wathq Employee Information API.
"""

import httpx

from app.core.config import settings
from .schemas import EmployeeInfoResponse


class WathqEmployeeClient:
    def __init__(self):
        self.base_url = "https://api.wathq.sa/masdr/employee"
        self.headers = {
            "apiKey": settings.WATHQ_API_KEY,
            "Content-Type": "application/json"
        }

    async def get_employee_info(self, employee_id: str) -> EmployeeInfoResponse:
        """Get employee information by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/info/{employee_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return EmployeeInfoResponse(**response.json())


employee_client = WathqEmployeeClient()