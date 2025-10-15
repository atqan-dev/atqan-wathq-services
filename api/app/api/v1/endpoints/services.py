"""
WATHQ Service management endpoints with tenant and user permissions.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps, management_deps
from app.core.permissions import require_permission

router = APIRouter()


@router.get("/wathq", response_model=schemas.ServiceListResponse)
def get_wathq_services(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all available WATHQ services.
    """
    services = crud.service.get_wathq_services(db=db)
    return schemas.ServiceListResponse(services=services, total=len(services))


@router.get("/wathq/management", response_model=schemas.ServiceListResponse)
def get_wathq_services_management(
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(management_deps.get_current_active_management_user),
) -> Any:
    """
    Get all available WATHQ services (management access).
    """
    services = crud.service.get_wathq_services(db=db)
    return schemas.ServiceListResponse(services=services, total=len(services))


@router.get("/tenant/my-services", response_model=schemas.TenantServiceListResponse)
def get_my_tenant_services(
    db: Session = Depends(deps.get_db),
    approved_only: bool = True,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get services for current user's tenant.
    """
    tenant_services = crud.tenant_service.get_tenant_services(
        db=db, tenant_id=current_user.tenant_id, approved_only=approved_only
    )
    return schemas.TenantServiceListResponse(
        tenant_services=tenant_services, total=len(tenant_services)
    )


@router.post("/tenant/request", response_model=schemas.TenantService)
def request_tenant_service(
    *,
    db: Session = Depends(deps.get_db),
    service_request: schemas.TenantServiceRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Request a service for current user's tenant.
    """
    require_permission(current_user, "manage_tenant_services")
    
    # Check if service exists
    service = crud.service.get(db=db, id=service_request.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    tenant_service = crud.tenant_service.request_tenant_service(
        db=db,
        tenant_id=current_user.tenant_id,
        service_id=service_request.service_id,
        max_users=service_request.max_users,
        wathq_api_key=service_request.wathq_api_key
    )
    return tenant_service


@router.post("/tenant/approve", response_model=schemas.TenantService)
def approve_tenant_service(
    *,
    db: Session = Depends(deps.get_db),
    approval: schemas.TenantServiceApproval,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Approve a tenant service request (admin only).
    """
    require_permission(current_user, "approve_service_requests")
    
    tenant_service = crud.tenant_service.approve_tenant_service(
        db=db,
        tenant_service_id=approval.tenant_service_id,
        approved_by=current_user.id
    )
    
    if not tenant_service:
        raise HTTPException(status_code=404, detail="Tenant service not found")
    
    return tenant_service


@router.get("/tenant/pending-approvals", response_model=schemas.TenantServiceListResponse)
def get_pending_approvals(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get pending service approval requests (admin only).
    """
    require_permission(current_user, "approve_service_requests")
    
    pending_services = crud.tenant_service.get_pending_approvals(db=db)
    return schemas.TenantServiceListResponse(
        tenant_services=pending_services, total=len(pending_services)
    )


@router.get("/user/my-services", response_model=schemas.UserAuthorizedServicesResponse)
def get_my_authorized_services(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get services current user is authorized to use.
    """
    services = crud.service.get_user_authorized_services(db=db, user_id=current_user.id)
    return schemas.UserAuthorizedServicesResponse(
        services=services, user_id=current_user.id
    )


@router.post("/user/assign", response_model=dict)
def assign_service_to_user(
    *,
    db: Session = Depends(deps.get_db),
    assignment: schemas.UserServiceAssignment,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Assign a service to a user (admin only).
    """
    require_permission(current_user, "assign_user_services")
    
    # Check if target user belongs to same tenant
    target_user = crud.user.get(db=db, id=assignment.user_id)
    if not target_user or target_user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign services to users from other tenants"
        )
    
    # Check if service is approved for tenant
    tenant_service = crud.tenant_service.get_by_tenant_and_service(
        db=db, tenant_id=current_user.tenant_id, service_id=assignment.service_id
    )
    if not tenant_service or not tenant_service.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service not approved for this tenant"
        )
    
    success = crud.service.assign_service_to_user(
        db=db, user_id=assignment.user_id, service_id=assignment.service_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign service to user"
        )
    
    return {"message": "Service assigned successfully"}


@router.delete("/user/revoke", response_model=dict)
def revoke_service_from_user(
    *,
    db: Session = Depends(deps.get_db),
    assignment: schemas.UserServiceAssignment,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Revoke a service from a user (admin only).
    """
    require_permission(current_user, "assign_user_services")
    
    # Check if target user belongs to same tenant
    target_user = crud.user.get(db=db, id=assignment.user_id)
    if not target_user or target_user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot revoke services from users in other tenants"
        )
    
    success = crud.service.revoke_service_from_user(
        db=db, user_id=assignment.user_id, service_id=assignment.service_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke service from user"
        )
    
    return {"message": "Service revoked successfully"}


@router.put("/tenant/update-api-key", response_model=schemas.TenantService)
def update_tenant_service_api_key(
    *,
    db: Session = Depends(deps.get_db),
    tenant_service_id: int,
    new_api_key: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update WATHQ API key for a tenant service.
    """
    require_permission(current_user, "manage_tenant_services")
    
    tenant_service = db.query(models.service.TenantService).filter(
        models.service.TenantService.id == tenant_service_id,
        models.service.TenantService.tenant_id == current_user.tenant_id
    ).first()
    
    if not tenant_service:
        raise HTTPException(status_code=404, detail="Tenant service not found")
    
    tenant_service.wathq_api_key = new_api_key
    db.commit()
    db.refresh(tenant_service)
    
    return tenant_service


@router.get("/{service_slug}", response_model=schemas.Service)
def get_service_by_slug(
    *,
    db: Session = Depends(deps.get_db),
    service_slug: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get service details by slug.
    """
    service = crud.service.get_by_slug(db=db, slug=service_slug)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.get("/management/my-services", response_model=schemas.ManagementServicesResponse)
def get_management_services(
    db: Session = Depends(deps.get_db),
    approved_only: bool = False,
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get services current user is authorized to use. (management access)
    """
    services = crud.tenant_service.get_management_all_services(db=db)
    return schemas.ManagementServicesResponse(
        services=services, total=len(services)
    )