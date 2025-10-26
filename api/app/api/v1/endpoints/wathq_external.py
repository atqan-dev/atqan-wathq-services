"""
API endpoints for WATHQ external service integration.
Separate endpoints for tenant users and management users.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app import models, schemas
from app.api import deps
from app.crud.crud_wathq_external_data import wathq_external_data
from app.services.wathq_external_service import wathq_external_service
from app.schemas.wathq_external_data import (
    WathqServiceRequest,
    WathqServiceResponse,
    WathqBulkServiceRequest,
    WathqBulkServiceResponse,
    WathqExternalData
)

# Create separate routers for tenant and management
tenant_router = APIRouter()
management_router = APIRouter()


# ============== TENANT USER ENDPOINTS ==============

@tenant_router.post("/call", response_model=WathqServiceResponse)
async def call_wathq_service_tenant(
    *,
    db: Session = Depends(deps.get_db),
    request: WathqServiceRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Call a WATHQ service (for tenant users).
    Data is cached per user/tenant combination.
    """
    # Check if user has permission to use the service
    service = db.query(models.Service).filter(
        models.Service.slug == request.service_slug
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check if tenant has access to this service
    if current_user.tenant_id:
        tenant_service = db.query(models.service.TenantService).filter(
            models.service.TenantService.tenant_id == current_user.tenant_id,
            models.service.TenantService.service_id == service.id,
            models.service.TenantService.is_active == True,
            models.service.TenantService.is_approved == True
        ).first()
        
        if not tenant_service:
            raise HTTPException(
                status_code=403,
                detail="Your tenant does not have access to this service"
            )
    
    # Check user permission
    permission_name = f"use_{request.service_slug.replace('-', '_')}"
    if not deps.has_permission(current_user, permission_name):
        raise HTTPException(
            status_code=403,
            detail=f"You don't have permission to use {service.name}"
        )
    
    # Call the service
    result = await wathq_external_service.get_service_data(
        db=db,
        user=current_user,
        service_slug=request.service_slug,
        params=request.params,
        force_refresh=request.force_refresh
    )
    
    return result


@tenant_router.post("/bulk", response_model=WathqBulkServiceResponse)
async def call_bulk_wathq_services_tenant(
    *,
    db: Session = Depends(deps.get_db),
    request: WathqBulkServiceRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Call multiple WATHQ services at once (for tenant users).
    """
    # Validate all services first
    for service_request in request.services:
        service = db.query(models.Service).filter(
            models.Service.slug == service_request.service_slug
        ).first()
        
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service '{service_request.service_slug}' not found"
            )
        
        # Check permissions for each service
        permission_name = f"use_{service_request.service_slug.replace('-', '_')}"
        if not deps.has_permission(current_user, permission_name):
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to use {service.name}"
            )
    
    # Call all services
    result = await wathq_external_service.get_bulk_service_data(
        db=db,
        user=current_user,
        service_requests=[r.dict() for r in request.services]
    )
    
    return result


@tenant_router.get("/cache", response_model=List[WathqExternalData])
def get_my_cached_data(
    *,
    db: Session = Depends(deps.get_db),
    service_id: Optional[UUID] = Query(None, description="Filter by service ID"),
    skip: int = 0,
    limit: int = Query(100, le=1000),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get my cached WATHQ data (for tenant users).
    """
    cached_data = wathq_external_data.get_user_cached_data(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        service_id=service_id,
        skip=skip,
        limit=limit
    )
    
    return cached_data


@tenant_router.delete("/cache")
def clear_my_cache(
    *,
    db: Session = Depends(deps.get_db),
    service_id: Optional[UUID] = Query(None, description="Service ID to clear"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Clear my cached WATHQ data (for tenant users).
    """
    count = wathq_external_data.clear_user_cache(
        db=db,
        user_id=current_user.id,
        service_id=service_id
    )
    
    return {"message": f"Cleared {count} cache entries"}


# ============== MANAGEMENT USER ENDPOINTS ==============

@management_router.get("/call", response_model=WathqServiceResponse)
async def call_wathq_service_management_get(
    *,
    db: Session = Depends(deps.get_db),
    service_slug: str = Query(..., description="Service slug to call"),
    tenant_id: Optional[int] = Query(None, description="Tenant ID for context"),
    force_refresh: bool = Query(False, description="Force refresh from external API"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Call a WATHQ service (for management users) - GET method.
    Management users can call any service without tenant restrictions.
    """
    try:
        # Create a pseudo-user for management context
        pseudo_user = models.User(
            id=current_user.id,
            email=current_user.email,
            tenant_id=tenant_id or 1,
            is_superuser=True,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            hashed_password="",
            is_active=True
        )
        
        # Call the service
        result = await wathq_external_service.get_service_data(
            db=db,
            user=pseudo_user,
            service_slug=service_slug,
            params={},
            force_refresh=force_refresh
        )
        
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calling WATHQ service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error calling WATHQ service: {str(e)}"
        )


@management_router.post("/call", response_model=WathqServiceResponse)
async def call_wathq_service_management(
    *,
    db: Session = Depends(deps.get_db),
    request: WathqServiceRequest,
    tenant_id: Optional[int] = Query(None, description="Tenant ID for context"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Call a WATHQ service (for management users) - POST method.
    Management users can call any service without tenant restrictions.
    """
    try:
        # Create a pseudo-user for management context
        pseudo_user = models.User(
            id=current_user.id,
            email=current_user.email,
            tenant_id=tenant_id or 1,
            is_superuser=True,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            hashed_password="",
            is_active=True
        )
        
        # Call the service
        result = await wathq_external_service.get_service_data(
            db=db,
            user=pseudo_user,
            service_slug=request.service_slug,
            params=request.params,
            force_refresh=request.force_refresh
        )
        
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calling WATHQ service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error calling WATHQ service: {str(e)}"
        )


@management_router.post("/bulk", response_model=WathqBulkServiceResponse)
async def call_bulk_wathq_services_management(
    *,
    db: Session = Depends(deps.get_db),
    request: WathqBulkServiceRequest,
    tenant_id: Optional[int] = Query(None, description="Tenant ID for context"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Call multiple WATHQ services at once (for management users).
    """
    # Create a pseudo-user for management context
    pseudo_user = models.User(
        id=current_user.id,
        email=current_user.email,
        tenant_id=tenant_id,
        is_superuser=True
    )
    
    # Call all services
    result = await wathq_external_service.get_bulk_service_data(
        db=db,
        user=pseudo_user,
        service_requests=[r.dict() for r in request.services]
    )
    
    return result


@management_router.get("/cache", response_model=List[WathqExternalData])
def get_cached_data_management(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: Optional[int] = Query(None, description="Filter by tenant ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    service_id: Optional[UUID] = Query(None, description="Filter by service ID"),
    skip: int = 0,
    limit: int = Query(100, le=1000),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get cached WATHQ data (for management users).
    Can view cache across all tenants and users.
    """
    if user_id:
        # Get specific user's cache
        cached_data = wathq_external_data.get_user_cached_data(
            db=db,
            user_id=user_id,
            tenant_id=tenant_id,
            service_id=service_id,
            skip=skip,
            limit=limit
        )
    elif tenant_id:
        # Get specific tenant's cache
        cached_data = wathq_external_data.get_tenant_cached_data(
            db=db,
            tenant_id=tenant_id,
            service_id=service_id,
            skip=skip,
            limit=limit
        )
    else:
        # Get all cache entries
        query = db.query(models.wathq_external_data.WathqExternalData)
        
        if service_id:
            query = query.filter(
                models.wathq_external_data.WathqExternalData.service_id == service_id
            )
        
        cached_data = query.offset(skip).limit(limit).all()
    
    return cached_data


@management_router.delete("/cache")
def clear_cache_management(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: Optional[int] = Query(None, description="Tenant ID to clear"),
    user_id: Optional[int] = Query(None, description="User ID to clear"),
    service_id: Optional[UUID] = Query(None, description="Service ID to clear"),
    expired_only: bool = Query(False, description="Clear only expired entries"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Clear cached WATHQ data (for management users).
    Can clear cache for any tenant/user or all expired entries.
    """
    if expired_only:
        count = wathq_external_data.clear_expired_cache(db=db)
        return {"message": f"Cleared {count} expired cache entries"}
    
    if user_id:
        count = wathq_external_data.clear_user_cache(
            db=db,
            user_id=user_id,
            service_id=service_id
        )
        return {"message": f"Cleared {count} cache entries for user {user_id}"}
    
    if tenant_id:
        count = wathq_external_data.clear_tenant_cache(
            db=db,
            tenant_id=tenant_id,
            service_id=service_id
        )
        return {"message": f"Cleared {count} cache entries for tenant {tenant_id}"}
    
    # Clear all cache
    count = db.query(models.wathq_external_data.WathqExternalData).count()
    db.query(models.wathq_external_data.WathqExternalData).delete()
    db.commit()
    
    return {"message": f"Cleared all {count} cache entries"}


@management_router.get("/stats")
def get_cache_statistics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get cache statistics (for management users).
    """
    from sqlalchemy import func
    from datetime import datetime
    
    total_entries = db.query(models.wathq_external_data.WathqExternalData).count()
    
    expired_entries = db.query(models.wathq_external_data.WathqExternalData).filter(
        models.wathq_external_data.WathqExternalData.expires_at <= datetime.utcnow()
    ).count()
    
    active_entries = total_entries - expired_entries
    
    # Get cache hit rate from call logs
    total_calls = db.query(models.WathqCallLog).count()
    cached_calls = db.query(models.WathqCallLog).filter(
        models.WathqCallLog.is_cached == True
    ).count()
    
    cache_hit_rate = (cached_calls / total_calls * 100) if total_calls > 0 else 0
    
    # Get top cached services
    top_services = db.query(
        models.Service.name,
        models.Service.slug,
        func.count(models.wathq_external_data.WathqExternalData.id).label('cache_count')
    ).join(
        models.wathq_external_data.WathqExternalData,
        models.Service.id == models.wathq_external_data.WathqExternalData.service_id
    ).group_by(
        models.Service.id, models.Service.name, models.Service.slug
    ).order_by(
        func.count(models.wathq_external_data.WathqExternalData.id).desc()
    ).limit(5).all()
    
    return {
        "total_cache_entries": total_entries,
        "active_cache_entries": active_entries,
        "expired_cache_entries": expired_entries,
        "total_api_calls": total_calls,
        "cached_api_calls": cached_calls,
        "cache_hit_rate": f"{cache_hit_rate:.2f}%",
        "top_cached_services": [
            {"name": s.name, "slug": s.slug, "count": s.cache_count}
            for s in top_services
        ]
    }
