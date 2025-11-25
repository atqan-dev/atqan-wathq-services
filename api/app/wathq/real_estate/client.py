"""
HTTP client for Wathq Real Estate API with tenant-specific keys and tracking.
"""

import httpx
from sqlalchemy.orm import Session

from app.core.wathq_tracker import WathqCallTracker
from .schemas import DeedResponse, IdType


class WathqRealEstateClient:
    def __init__(self, api_key: str, db: Session, tenant_id: int, user_id: int):
        self.base_url = "https://api.wathq.sa/moj/real-estate"
        self.api_key = api_key
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.service_slug = "real-estate"
        
        if not api_key:
            raise ValueError(f"No WATHQ API key found for tenant {tenant_id} and service {self.service_slug}")
            
        self.headers = {
            "apiKey": api_key,
            "Content-Type": "application/json"
        }

    async def get_deed_details(
        self, 
        deed_number: int, 
        id_number: str, 
        id_type: IdType
    ) -> DeedResponse:
        """Get real estate deed details with tracking."""
        endpoint = f"/deed/{deed_number}/{id_number}/{id_type.value}"
        
        with WathqCallTracker.track_call(
            db=self.db,
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            service_slug=self.service_slug,
            endpoint=endpoint,
            method="GET"
        ) as tracker:
            
            request_data = {
                "deed_number": deed_number,
                "id_number": id_number,
                "id_type": id_type.value
            }
            tracker.set_request_data(request_data)
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        timeout=30.0
                    )
                    
                    response_data = response.json()
                    tracker.log_response(response.status_code, response_data)
                    
                    response.raise_for_status()
                    return DeedResponse(**response_data)
                    
            except Exception as e:
                error_response = {"error": str(e), "type": type(e).__name__}
                tracker.log_response(getattr(e, 'response', {}).get('status_code', 500), error_response)
                raise