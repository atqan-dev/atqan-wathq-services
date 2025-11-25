"""
Service layer for WATHQ external API integration.
Handles caching, external API calls, and data management.
"""

import httpx
from typing import Optional, Dict, Any, List
import logging

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.service import Service
from app.models.wathq_call_log import WathqCallLog
from app.crud.crud_wathq_external_data import wathq_external_data
from app.core.config import settings

logger = logging.getLogger(__name__)


class WathqExternalService:
    """Service for handling WATHQ external API calls with caching."""
    
    def __init__(self):
        self.base_url = settings.WATHQ_API_BASE_URL if hasattr(settings, 'WATHQ_API_BASE_URL') else "https://api.wathq.sa/v1"
        self.timeout = 30  # seconds
        
    def _get_service_endpoint(self, service_slug: str) -> str:
        """Get the external API endpoint for a service."""
        # Map service slugs to WATHQ API endpoints
        endpoints = {
            "commercial-registration": "/commercial/verify",
            "real-estate": "/realestate/property",
            "employee-verification": "/employment/verify",
            "company-contract": "/contracts/verify",
            "attorney-services": "/legal/attorney",
            "national-address": "/address/verify"
        }
        return endpoints.get(service_slug, f"/{service_slug}")
    
    def _get_api_key(self, db: Session, user: User, service: Service) -> Optional[str]:
        """Get the appropriate API key for the service."""
        # Check for tenant-specific API key
        if user.tenant_id:
            from app.models.service import TenantService
            tenant_service = db.query(TenantService).filter(
                TenantService.tenant_id == user.tenant_id,
                TenantService.service_id == service.id,
                TenantService.is_active == True,
                TenantService.is_approved == True
            ).first()
            
            if tenant_service and tenant_service.wathq_api_key:
                return tenant_service.wathq_api_key
        
        # Fallback to system API key
        return settings.WATHQ_API_KEY if hasattr(settings, 'WATHQ_API_KEY') else None
    
    async def _call_external_api(
        self,
        endpoint: str,
        params: Dict[str, Any],
        api_key: str,
        method: str = "GET"
    ) -> tuple[Dict[str, Any], int]:
        """Make actual call to external WATHQ API."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method == "POST":
                    response = await client.post(url, json=params, headers=headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                return response.json(), response.status_code
                
            except httpx.TimeoutException:
                logger.error(f"Timeout calling WATHQ API: {url}")
                return {"error": "API timeout", "message": "External service timeout"}, 504
            except httpx.RequestError as e:
                logger.error(f"Error calling WATHQ API: {url} - {str(e)}")
                return {"error": "API error", "message": str(e)}, 503
            except Exception as e:
                logger.error(f"Unexpected error calling WATHQ API: {str(e)}")
                return {"error": "Internal error", "message": str(e)}, 500
    
    def _log_api_call(
        self,
        db: Session,
        user: User,
        service: Service,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        status_code: int,
        cached: bool
    ):
        """Log the API call for auditing."""
        try:
            log_entry = WathqCallLog(
                tenant_id=user.tenant_id,
                user_id=user.id,
                service_id=service.id,
                endpoint=self._get_service_endpoint(service.slug),
                request_data=request_data,
                response_data=response_data,
                status_code=status_code,
                is_cached=cached
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log API call: {str(e)}")
            db.rollback()
    
    async def get_service_data(
        self,
        db: Session,
        user: User,
        service_slug: str,
        params: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get data from WATHQ service with caching.
        
        Args:
            db: Database session
            user: Current user
            service_slug: Service to call
            params: Service-specific parameters
            force_refresh: Force fetch from external API
            
        Returns:
            Dict containing the service response
        """
        # Get service details
        service = db.query(Service).filter(Service.slug == service_slug).first()
        if not service:
            return {
                "status": "error",
                "message": f"Service '{service_slug}' not found",
                "cached": False
            }
        
        # Check if service is active
        if not service.is_active:
            return {
                "status": "error",
                "message": f"Service '{service_slug}' is not active",
                "cached": False
            }
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = wathq_external_data.get_cached_data(
                db=db,
                service_id=service.id,
                tenant_id=user.tenant_id,
                user_id=user.id,
                params=params
            )
            
            if cached_data:
                # Log the cached response
                self._log_api_call(
                    db, user, service, params or {},
                    cached_data.data, 200, True
                )
                
                return {
                    "service": service_slug,
                    "data": cached_data.data,
                    "cached": True,
                    "cache_expires_at": cached_data.expires_at,
                    "status": "success"
                }
        
        # Get API key
        api_key = self._get_api_key(db, user, service)
        if not api_key:
            return {
                "status": "error",
                "message": "No API key configured for this service",
                "cached": False
            }
        
        # Call external API
        endpoint = self._get_service_endpoint(service_slug)
        response_data, status_code = await self._call_external_api(
            endpoint, params or {}, api_key
        )
        
        # Save to cache if successful
        if status_code == 200:
            cached_entry = wathq_external_data.save_external_data(
                db=db,
                service_id=service.id,
                tenant_id=user.tenant_id,
                user_id=user.id,
                data=response_data,
                params=params,
                status_code=status_code,
                ttl_seconds=service.cache_ttl if hasattr(service, 'cache_ttl') else 3600
            )
            
            # Log the API call
            self._log_api_call(
                db, user, service, params or {},
                response_data, status_code, False
            )
            
            return {
                "service": service_slug,
                "data": response_data,
                "cached": False,
                "cache_expires_at": cached_entry.expires_at,
                "status": "success"
            }
        else:
            # Log the failed API call
            self._log_api_call(
                db, user, service, params or {},
                response_data, status_code, False
            )
            
            return {
                "service": service_slug,
                "data": response_data,
                "cached": False,
                "status": "error",
                "message": f"External API returned status {status_code}"
            }
    
    async def get_bulk_service_data(
        self,
        db: Session,
        user: User,
        service_requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get data from multiple WATHQ services.
        
        Args:
            db: Database session
            user: Current user
            service_requests: List of service requests
            
        Returns:
            Dict containing all service responses
        """
        results = []
        successful = 0
        failed = 0
        
        for request in service_requests:
            result = await self.get_service_data(
                db=db,
                user=user,
                service_slug=request.get("service_slug"),
                params=request.get("params"),
                force_refresh=request.get("force_refresh", False)
            )
            
            results.append(result)
            
            if result.get("status") == "success":
                successful += 1
            else:
                failed += 1
        
        return {
            "results": results,
            "total_requested": len(service_requests),
            "successful": successful,
            "failed": failed
        }


# Singleton instance
wathq_external_service = WathqExternalService()
