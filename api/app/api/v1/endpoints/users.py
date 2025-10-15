"""
User management endpoints.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users from current tenant.
    """
    users = crud.user.get_users_by_tenant(
        db, tenant_id=current_user.tenant_id, skip=skip, limit=limit
    )
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new user in the current tenant. Only superusers can create users.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    # Check if user already exists in this tenant
    user = crud.user.get_by_email(
        db, email=user_in.email, tenant_id=current_user.tenant_id
    )
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the tenant.",
        )

    user = crud.user.create(db, obj_in=user_in, tenant_id=current_user.tenant_id)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id within the same tenant.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user belongs to the same tenant
    if user.tenant_id != current_user.tenant_id and not current_user.is_superuser:
        raise HTTPException(status_code=404, detail="User not found")

    return user
