"""
Authentication endpoints with multitenancy support.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.multitenancy import get_current_tenant

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login with tenant support.
    Tenant is identified from the request context (subdomain, header, etc.)
    """
    # Get tenant from context
    current_tenant = get_current_tenant()
    tenant_slug = current_tenant.tenant_slug
    tenant_id = current_tenant.tenant_id

    if tenant_slug and tenant_id:
        # Verify tenant is active
        tenant = crud.tenant.get(db, id=tenant_id)
        if not tenant or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant not found or inactive",
            )

    # Authenticate user within tenant context
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password, tenant_id=tenant_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create access token with tenant information
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id,
        tenant_id=tenant_id,
        tenant_slug=tenant_slug,
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=schemas.User)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Register new user in the current tenant context.
    """
    # Get tenant from context
    current_tenant = get_current_tenant()
    tenant_slug = current_tenant.tenant_slug
    tenant_id = current_tenant.tenant_id
    
    if not tenant_slug or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context required for user registration",
        )

    # Get tenant info
    tenant = crud.tenant.get(db, id=tenant_id)
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant not found or inactive",
        )

    # Check user limit
    existing_users_count = len(
        crud.user.get_users_by_tenant(db, tenant_id=tenant.id)
    )
    if existing_users_count >= tenant.max_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant has reached maximum user limit",
        )

    # Check if user already exists in this tenant
    user = crud.user.get_by_email(db, email=user_in.email, tenant_id=tenant.id)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the tenant.",
        )

    # Create user in tenant context
    user = crud.user.create(db, obj_in=user_in, tenant_id=tenant_id)

    # Assign default role to new user
    default_role = crud.role.get_default_role_for_tenant(db, tenant_id=tenant.id)
    if default_role:
        crud.role.assign_to_user(db, role_id=default_role.id, user_id=user.id)

    return user


@router.post("/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token and return current user with tenant info.
    """
    return current_user


@router.post("/logout")
def logout(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Logout endpoint - invalidate token (client-side handling).
    """
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(
    refresh_data: dict,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Refresh access token using refresh token.
    Note: This is a simplified implementation.
    In production, you should store and validate refresh tokens.
    """
    # For now, we'll create a new token
    # In production, validate the refresh token first
    try:
        # Decode the refresh token to get user info
        refresh_token = refresh_data.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token required",
            )
        payload = security.decode_token(refresh_token)
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        tenant_slug = payload.get("tenant_slug")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        # Get user from database
        user = crud.user.get(db, id=user_id)
        if not user or not crud.user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=user.id,
            tenant_id=tenant_id,
            tenant_slug=tenant_slug,
            expires_delta=access_token_expires,
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
