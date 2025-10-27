"""
Management endpoints for cross-tenant administration.
"""

from typing import Any
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.api.management_deps import (
    get_current_active_management_user,
    get_current_super_admin,
)
from app.core.config import settings
from app.models.management_user import ManagementUser
from app.models.management_user_profile import ManagementUserProfile

router = APIRouter()


# Dashboard Stats
@router.get("/stats")
def get_management_stats(
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get management dashboard statistics.
    Returns counts for tenants, users, online requests, and offline requests.
    """
    try:
        from app.models.tenant import Tenant
        from app.models.user import User
        from app.models.wathq_call_log import WathqCallLog
        from app.models.wathq_offline_data import WathqOfflineData

        # Count all tenants
        tenants_count = db.query(Tenant).count()

        # Count all users across all tenants
        users_count = db.query(User).count()

        # Count all online requests (WATHQ call logs)
        online_requests_count = db.query(WathqCallLog).count()

        # Count all offline requests (WATHQ offline data)
        offline_requests_count = db.query(WathqOfflineData).count()

        return {
            "tenants_count": tenants_count,
            "users_count": users_count,
            "online_requests_count": online_requests_count,
            "offline_requests_count": offline_requests_count,
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching management stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching management stats: {str(e)}"
        )


# Management Users CRUD
@router.get("/users/me", response_model=schemas.ManagementUser)
def read_current_management_user(
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Get current management user."""
    return current_user


@router.get("/users", response_model=list[schemas.ManagementUser])
def read_management_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Retrieve management users."""
    users = crud.management_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/users", response_model=schemas.ManagementUser)
def create_management_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.ManagementUserCreate,
    current_user: ManagementUser = Depends(get_current_super_admin),
) -> Any:
    """Create new management user (Super Admin only)."""

    user = crud.management_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.management_user.create(db, obj_in=user_in)
    return user


@router.put("/users/{user_id}", response_model=schemas.ManagementUser)
def update_management_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.ManagementUserUpdate,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Update management user (Super Admin or self only)."""

    # Check if user is super admin or updating their own profile
    if (
        not crud.management_user.is_super_admin(current_user)
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges or self access required",
        )

    user = crud.management_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.management_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/users/{user_id}")
def delete_management_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: ManagementUser = Depends(get_current_super_admin),
) -> Any:
    """Delete management user (Super Admin only)."""

    user = crud.management_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.management_user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/activate")
def activate_management_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: ManagementUser = Depends(get_current_super_admin),
) -> Any:
    """Activate management user (Super Admin only)."""

    user = crud.management_user.activate(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User activated successfully"}


@router.post("/users/{user_id}/deactivate")
def deactivate_management_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: ManagementUser = Depends(get_current_super_admin),
) -> Any:
    """Deactivate management user (Super Admin only)."""

    user = crud.management_user.deactivate(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deactivated successfully"}


# Tenant Management
@router.get("/tenants", response_model=list[schemas.Tenant])
def read_tenants(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Retrieve all tenants."""
    tenants = crud.tenant.get_multi(db, skip=skip, limit=limit)
    return tenants


@router.post("/tenants", response_model=schemas.Tenant)
def create_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_in: schemas.TenantCreate,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Create new tenant."""
    tenant = crud.tenant.get_by_slug(db, slug=tenant_in.slug)
    if tenant:
        raise HTTPException(
            status_code=400,
            detail="The tenant with this slug already exists in the system.",
        )
    tenant = crud.tenant.create(db, obj_in=tenant_in)
    return tenant


@router.put("/tenants/{tenant_id}", response_model=schemas.Tenant)
def update_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
    tenant_in: schemas.TenantUpdate,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Update tenant."""
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant = crud.tenant.update(db, db_obj=tenant, obj_in=tenant_in)
    return tenant


@router.post("/tenants/{tenant_id}/activate")
def activate_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Activate tenant."""
    tenant = crud.tenant.activate(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant activated successfully"}


@router.post("/tenants/{tenant_id}/deactivate")
def deactivate_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Deactivate tenant."""
    tenant = crud.tenant.deactivate(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant deactivated successfully"}


# Regular Users Management (Cross-tenant)
@router.get("/all-users", response_model=list[schemas.User])
def read_all_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    tenant_id: int = None,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Retrieve all users across tenants."""
    if tenant_id:
        users = crud.user.get_users_by_tenant(
            db, tenant_id=tenant_id, skip=skip, limit=limit
        )
    else:
        users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/regular-users/{user_id}/activate")
def activate_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Activate regular user."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.add(user)
    db.commit()
    return {"message": "User activated successfully"}


@router.post("/regular-users/{user_id}/deactivate")
def deactivate_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Deactivate regular user."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.add(user)
    db.commit()
    return {"message": "User deactivated successfully"}


# Management User Profiles
# NOTE: /users/me/profile routes MUST come before /users/{user_id}/profile
# to avoid FastAPI treating "me" as a user_id parameter

@router.get("/users/me/profile", response_model=schemas.ManagementUserProfile)
def read_current_management_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    request: Request,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Get current management user's profile (convenience endpoint)."""
    
    profile = (
        db.query(ManagementUserProfile)
        .filter(ManagementUserProfile.management_user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Convert relative avatar URL to full URL
    if profile.avatar_image_url:
        profile.avatar_image_url = (
            str(request.base_url).rstrip("/") + profile.avatar_image_url
        )

    return profile


@router.post("/users/me/profile", response_model=schemas.ManagementUserProfile)
def create_current_management_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: schemas.ManagementUserProfileCreate,
    request: Request,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Create current management user's profile (self-service)."""

    # Check if profile already exists
    existing_profile = (
        db.query(ManagementUserProfile)
        .filter(ManagementUserProfile.management_user_id == current_user.id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=400, detail="Profile already exists for this user"
        )

    profile = ManagementUserProfile(
        management_user_id=current_user.id,
        fullname=profile_in.fullname,
        address=profile_in.address,
        mobile=profile_in.mobile,
        city=profile_in.city,
        company_name=profile_in.company_name,
        commercial_registration_number=profile_in.commercial_registration_number,
        entity_number=profile_in.entity_number,
        full_info=profile_in.full_info,
        email=profile_in.email,
        whatsapp_number=profile_in.whatsapp_number,
        avatar_image_url=profile_in.avatar_image_url,
        is_active=profile_in.is_active,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Convert relative avatar URL to full URL
    if profile.avatar_image_url:
        profile.avatar_image_url = (
            str(request.base_url).rstrip("/") + profile.avatar_image_url
        )

    return profile


@router.put("/users/me/profile", response_model=schemas.ManagementUserProfile)
def update_current_management_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: schemas.ManagementUserProfileUpdate,
    request: Request,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Update current management user's profile (convenience endpoint)."""

    profile = (
        db.query(ManagementUserProfile)
        .filter(ManagementUserProfile.management_user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update profile fields
    profile_data = profile_in.dict(exclude_unset=True)
    for field, value in profile_data.items():
        if value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    # Convert relative avatar URL to full URL
    if profile.avatar_image_url:
        profile.avatar_image_url = (
            str(request.base_url).rstrip("/") + profile.avatar_image_url
        )

    return profile


# Admin-controlled profile endpoints (for managing other users)
@router.post("/users/{user_id}/profile", response_model=schemas.ManagementUserProfile)
def create_management_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    profile_in: schemas.ManagementUserProfileCreate,
    request: Request,
    current_user: ManagementUser = Depends(get_current_super_admin),
) -> Any:
    """Create management user profile (Super Admin only)."""

    user = crud.management_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if profile already exists
    existing_profile = (
        db.query(ManagementUserProfile)
        .filter(ManagementUserProfile.management_user_id == user_id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=400, detail="Profile already exists for this user"
        )

    profile = ManagementUserProfile(
        management_user_id=user_id,
        fullname=profile_in.fullname,
        address=profile_in.address,
        mobile=profile_in.mobile,
        city=profile_in.city,
        company_name=profile_in.company_name,
        commercial_registration_number=profile_in.commercial_registration_number,
        entity_number=profile_in.entity_number,
        full_info=profile_in.full_info,
        email=profile_in.email,
        whatsapp_number=profile_in.whatsapp_number,
        avatar_image_url=profile_in.avatar_image_url,
        is_active=profile_in.is_active,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Convert relative avatar URL to full URL
    if profile.avatar_image_url:
        profile.avatar_image_url = (
            str(request.base_url).rstrip("/") + profile.avatar_image_url
        )

    return profile


@router.get("/users/{user_id}/profile", response_model=schemas.ManagementUserProfile)
def read_management_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    request: Request,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Get management user profile."""

    # Super admins can view any profile, regular management users can only view their own
    if (
        not crud.management_user.is_super_admin(current_user)
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges or self access required",
        )

    profile = (
        db.query(ManagementUserProfile)
        .filter(ManagementUserProfile.management_user_id == user_id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Convert relative avatar URL to full URL
    if profile.avatar_image_url:
        profile.avatar_image_url = (
            str(request.base_url).rstrip("/") + profile.avatar_image_url
        )

    return profile


@router.put("/users/{user_id}/profile", response_model=schemas.ManagementUserProfile)
def update_management_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    profile_in: schemas.ManagementUserProfileUpdate,
    request: Request,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Update management user profile."""

    # Super admins can update any profile, regular management users can only update their own
    if (
        not crud.management_user.is_super_admin(current_user)
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges or self access required",
        )

    profile = (
        db.query(ManagementUserProfile)
        .filter(ManagementUserProfile.management_user_id == user_id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update profile fields
    profile_data = profile_in.dict(exclude_unset=True)
    for field, value in profile_data.items():
        if value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    # Convert relative avatar URL to full URL
    if profile.avatar_image_url:
        profile.avatar_image_url = (
            str(request.base_url).rstrip("/") + profile.avatar_image_url
        )

    return profile


@router.put("/avatar", response_model=schemas.ManagementUserProfile)
async def update_management_user_avatar(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    request: Request,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """Update current management user's avatar by uploading an image file."""

    # Validate file type
    if file.content_type not in settings.ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_AVATAR_TYPES)}",
        )

    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_AVATAR_SIZE} bytes",
        )

    # Get user profile
    profile = (
        db.query(ManagementUserProfile)
        .filter(ManagementUserProfile.management_user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Create uploads directory if it doesn't exist
    avatars_dir = Path(settings.AVATARS_DIR)
    avatars_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{current_user.id}_{uuid.uuid4()}.{file_extension}"
    file_path = avatars_dir / unique_filename

    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    # Generate file URL (relative to server root)
    avatar_url = f"/uploads/avatars/{unique_filename}"

    # Update profile with new avatar URL
    profile.avatar_image_url = avatar_url

    db.commit()
    db.refresh(profile)

    # Convert relative avatar URL to full URL
    if profile.avatar_image_url:
        profile.avatar_image_url = (
            str(request.base_url).rstrip("/") + profile.avatar_image_url
        )

    return profile


# Tenant routes - static routes MUST come before parameterized routes
@router.get("/tenants/services", response_model=list[schemas.TenantService])
def get_tenant_all_assigned_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get all services assigned to all tenants.
    """
    tenant_services = crud.tenant_service.get_management_all_services(
        db, skip=skip, limit=limit
    )
    return tenant_services


@router.get("/tenants/users", response_model=list[schemas.User])
def get_all_tenant_users_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get all users for all tenants.
    """
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/tenants/history", response_model=list[schemas.WathqCallLog])
def get_tenant_all_wathq_call_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get all WATHQ call logs for all tenants.
    """
    try:
        call_logs = crud.wathq_call_log.get_all(db, skip=skip, limit=limit)
        return call_logs
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching WATHQ call logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching WATHQ call logs: {str(e)}"
        )


@router.get(
    "/tenants/wathq-offline-data", response_model=list[schemas.WathqOfflineData]
)
def get_tenant_all_wathq_offline_data(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get all WATHQ offline data for all tenants.
    """
    try:
        offline_data = crud.wathq_offline_data.get_all(db, skip=skip, limit=limit)
        return offline_data
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching WATHQ offline data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching WATHQ offline data: {str(e)}"
        )


@router.get("/tenants/{tenant_id}", response_model=schemas.Tenant)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get tenant by ID.
    """
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    return tenant


@router.get("/tenants/{tenant_id}/users", response_model=list[schemas.User])
def get_tenant_users(
    tenant_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get users by tenant ID.
    """
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    users = crud.user.get_users_by_tenant(
        db, tenant_id=tenant.id, skip=skip, limit=limit
    )
    return users


@router.get("/tenants/{tenant_id}/stats")
def get_tenant_stats(
    tenant_id: int,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get users by tenant ID.
    """
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    user_count = crud.user.get_user_count_by_tenant(db, tenant_id=tenant.id)
    #  tenantStats.userCount = response.user_count;
    # tenantStats.activeServices = response.active_services;
    # tenantStats.activeServices = response.active_services;
    active_services = crud.tenant_service.get_active_services_by_tenant(
        db, tenant_id=tenant.id
    )
    data = {
        "user_count": user_count,
        "active_services": active_services,
    }
    return data


# Service Management
@router.get("/services", response_model=list[schemas.Service])
def get_all_services(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get all services for management users.
    """
    services = crud.service.get_multi(db, skip=skip, limit=limit)
    return services


@router.post("/tenants/{tenant_id}/services", response_model=schemas.TenantService)
def assign_service_to_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
    service_request: schemas.TenantServiceRequest,
    current_user: ManagementUser = Depends(get_current_super_admin),
) -> Any:
    """
    Assign a service to a tenant (Super Admin only).
    """
    # Check if tenant exists
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check if service exists
    service = crud.service.get(db, id=service_request.service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    # Check if service is already assigned to tenant
    existing_assignment = crud.tenant_service.get_by_tenant_and_service(
        db, tenant_id=tenant_id, service_id=service_request.service_id
    )
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service is already assigned to this tenant",
        )

    # Create tenant service assignment
    tenant_service = crud.tenant_service.request_tenant_service(
        db,
        tenant_id=tenant_id,
        service_id=service_request.service_id,
        max_users=service_request.max_users,
        wathq_api_key=service_request.wathq_api_key,
    )

    return tenant_service


@router.get("/tenants/{tenant_id}/services", response_model=list[schemas.TenantService])
def get_tenant_assigned_services(
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    approved_only: bool = True,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get all services assigned to a specific tenant.
    """
    # Check if tenant exists
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    tenant_services = crud.tenant_service.get_tenant_services(
        db, tenant_id=tenant_id, approved_only=approved_only
    )

    # Apply pagination manually since get_tenant_services doesn't support it directly
    start_idx = skip
    end_idx = start_idx + limit
    paginated_services = tenant_services[start_idx:end_idx]

    return paginated_services


# Tenant User Management
@router.post("/tenants/{tenant_id}/users", response_model=schemas.User)
def create_user_for_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
    user_in: schemas.UserCreate,
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Create a new user for a specific tenant.
    """
    # Check if tenant exists
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check if user with this email already exists in the tenant
    existing_user = crud.user.get_by_email(db, email=user_in.email, tenant_id=tenant_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists in the tenant",
        )

    # Create user for the tenant
    user = crud.user.create(db, obj_in=user_in, tenant_id=tenant_id)
    return user


@router.put("/users/{user_id}/tenant", response_model=schemas.User)
def update_user_tenant(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    new_tenant_id: int,
    current_user: ManagementUser = Depends(get_current_super_admin),
) -> Any:
    """
    Update a user's tenant assignment (Super Admin only).
    """
    # Check if user exists
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if new tenant exists
    new_tenant = crud.tenant.get(db, id=new_tenant_id)
    if not new_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New tenant not found",
        )

    # Prevent moving to same tenant
    if user.tenant_id == new_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already in this tenant",
        )

    # Update user's tenant
    user.tenant_id = new_tenant_id
    db.commit()
    db.refresh(user)

    return user


# WATHQ Data Management
@router.get("/tenants/{tenant_id}/history", response_model=list[schemas.WathqCallLog])
def get_tenant_wathq_call_logs(
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get all WATHQ call logs for a specific tenant.
    """
    # Check if tenant exists
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    call_logs = crud.wathq_call_log.get_by_tenant(
        db, tenant_id=tenant_id, skip=skip, limit=limit
    )
    return call_logs


@router.get(
    "/tenants/{tenant_id}/wathq-offline-data",
    response_model=list[schemas.WathqOfflineData],
)
def get_tenant_wathq_offline_data(
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get all WATHQ offline data for a specific tenant.
    """
    # Check if tenant exists
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    offline_data = crud.wathq_offline_data.get_by_tenant(
        db, tenant_id=tenant_id, skip=skip, limit=limit
    )
    return offline_data


# Get tenant user by tenant_id/ user_id
@router.get("/tenants/{tenant_id}/users/{user_id}", response_model=schemas.User)
def get_tenant_user(
    tenant_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Get a specific user for a specific tenant.
    """
    # Check if user exists
    user = crud.user.get(db, id=user_id, tenant_id=tenant_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if user belongs to the tenant
    if user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant",
        )

    return user


# update tenant user by tenant_id/ user_id
@router.put("/tenants/{tenant_id}/users/{user_id}", response_model=schemas.User)
def update_tenant_user(
    tenant_id: int,
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Update a specific user for a specific tenant.
    """
    # Check if user exists
    user = crud.user.get(db, id=user_id, tenant_id=tenant_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if user belongs to the tenant
    if user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant",
        )

    # Update user
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/tenants/{tenant_id}/users/{user_id}", response_model=schemas.User)
def delete_tenant_user(
    tenant_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Delete a specific user for a specific tenant.
    """
    # Check if user exists
    user = crud.user.get(db, id=user_id, tenant_id=tenant_id)
    old_user_email = user.email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if user belongs to the tenant
    if user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant",
        )

    # Delete user
    user = crud.user.remove(db, id=user_id)
    return {
        "message": "User deleted successfully",
        "user": old_user_email,
    }

@router.patch("/tenants/{tenant_id}/services/{service_id}/approve", response_model=schemas.TenantService)
def approve_tenant_service(
    tenant_id: int,
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Approve a specific service for a specific tenant.
    """
    # Check if service is assigned to the tenant
    tenant_service = crud.tenant_service.get(
        db, id=service_id
    )
    if not tenant_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not assigned to this tenant",
        )
    # Check if tenant exists
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check if service is assigned to the tenant
    if tenant_service.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service not assigned to this tenant",
        )

    # Check if service exists
    service = crud.service.get(db, id=tenant_service.service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    # Approve service
    tenant_service.is_approved = True
    db.add(tenant_service)
    db.commit()
    db.refresh(tenant_service)
    return tenant_service


# PUT http://127.0.0.1:5501/api/v1/management/tenants/services/2
@router.put("/tenants/services/{service_id}", response_model=schemas.TenantService)
def update_tenant_service(
    service_id: int,
    tenant_service_in: schemas.TenantServiceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Update a specific service for a specific tenant.
    """
    # Check if service is assigned to the tenant
    tenant_service = crud.tenant_service.get(
        db, id=service_id
    )
    if not tenant_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not assigned to this tenant",
        )

    # Update tenant service with provided data
    tenant_service = crud.tenant_service.update(
        db, db_obj=tenant_service, obj_in=tenant_service_in
    )
    return tenant_service


@router.delete("/tenants/services/{service_id}", response_model=schemas.TenantService)
def delete_tenant_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> Any:
    """
    Delete a specific service for a specific tenant.
    """
    # Check if service is assigned to the tenant
    tenant_service = crud.tenant_service.get(
        db, id=service_id
    )
    if not tenant_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not assigned to this tenant",
        )
    # Delete tenant service
    tenant_service = crud.tenant_service.remove(db, id=service_id)
    return {
        "message": "Service deleted successfully",
        "service": tenant_service,
        "tenant_id": tenant_service.tenant_id,
        "service_id": tenant_service.service_id,
    }
        