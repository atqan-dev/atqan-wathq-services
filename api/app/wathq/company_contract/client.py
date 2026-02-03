"""
HTTP client for Wathq Company Contract API.

Based on Wathq OpenAPI Spec v2.0.0
Host: api.wathq.sa
BasePath: /company-contract
"""

import httpx
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class WathqAPIError(Exception):
    """Wathq API error with status code and message."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{status_code}: {message}")


class WathqCompanyContractClient:
    """HTTP client for Wathq Company Contract API."""

    BASE_URL = "https://api.wathq.sa/company-contract"
    TIMEOUT = 30.0

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required for Wathq Company Contract API")
        self.api_key = api_key
        self.headers = {
            "apiKey": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """Make HTTP request to Wathq API with robust error handling."""
        url = f"{self.BASE_URL}{endpoint}"

        # Filter out None values from params
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        logger.debug(f"Wathq API request: {method} {url} params={clean_params}")

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.request(
                    method=method, url=url, headers=self.headers, params=clean_params
                )

                # Handle different error status codes per OpenAPI spec
                if response.status_code == 400:
                    error_msg = self._extract_error_message(
                        response, "Bad Request - Invalid parameters"
                    )
                    raise WathqAPIError(400, error_msg)
                elif response.status_code == 401:
                    raise WathqAPIError(
                        401, "Unauthorized - Invalid or missing API key"
                    )
                elif response.status_code == 404:
                    error_msg = self._extract_error_message(
                        response, "Not Found - CR not found or no contract data"
                    )
                    raise WathqAPIError(404, error_msg)
                elif response.status_code == 500:
                    raise WathqAPIError(
                        500, "Internal Server Error - Wathq API unavailable"
                    )
                elif response.status_code != 200:
                    error_msg = self._extract_error_message(
                        response, f"HTTP {response.status_code}"
                    )
                    raise WathqAPIError(response.status_code, error_msg)

                return response.json()

        except httpx.TimeoutException:
            raise WathqAPIError(
                408, "Request timeout - Wathq API did not respond in time"
            )
        except httpx.ConnectError:
            raise WathqAPIError(503, "Connection error - Unable to reach Wathq API")
        except WathqAPIError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error calling Wathq API: {e}")
            raise WathqAPIError(500, f"Unexpected error: {str(e)}")

    def _extract_error_message(self, response: httpx.Response, default: str) -> str:
        """Extract error message from API response."""
        try:
            error_data = response.json()
            return (
                error_data.get("message")
                or error_data.get("error")
                or error_data.get("code")
                or default
            )
        except Exception:
            return response.text[:200] if response.text else default

    async def get_contract_info(
        self,
        cr_national_number: str,
        language: str = "ar",
        copy_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get company contract information."""
        params = {"language": language}
        if copy_number:
            params["copyNumber"] = copy_number
        return await self._make_request(f"/info/{cr_national_number}", params)

    async def get_management_info(
        self, cr_national_number: str, language: str = "ar"
    ) -> Dict[str, Any]:
        """Get management information."""
        return await self._make_request(
            f"/management/{cr_national_number}", {"language": language}
        )

    async def get_manager_info(
        self,
        cr_national_number: str,
        manager_id: str,
        id_type: str,
        permission_id: Optional[str] = None,
        language: str = "ar",
    ) -> Dict[str, Any]:
        """Get manager information with permissions."""
        params = {"language": language}
        if permission_id:
            params["permissionId"] = permission_id
        return await self._make_request(
            f"/manager/{cr_national_number}/{manager_id}/{id_type}", params
        )

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
