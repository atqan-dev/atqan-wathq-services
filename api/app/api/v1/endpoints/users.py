"""
User management endpoints.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=list[schemas.UserWithRoles])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    is_active: bool | None = None,
    role_id: int | None = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users from current tenant with optional filtering.
    """
    query = db.query(models.User).filter(models.User.tenant_id == current_user.tenant_id)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.User.email.ilike(search_filter)) |
            (models.User.first_name.ilike(search_filter)) |
            (models.User.last_name.ilike(search_filter))
        )
    
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    
    if role_id is not None:
        query = query.join(models.User.roles).filter(models.permission.Role.id == role_id)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/count", response_model=int)
def count_users(
    db: Session = Depends(deps.get_db),
    search: str | None = None,
    is_active: bool | None = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get total count of users in current tenant.
    """
    query = db.query(models.User).filter(models.User.tenant_id == current_user.tenant_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.User.email.ilike(search_filter)) |
            (models.User.first_name.ilike(search_filter)) |
            (models.User.last_name.ilike(search_filter))
        )
    
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    
    return query.count()


@router.post("/", response_model=schemas.UserWithRoles)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreateWithRoles,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new user in the current tenant. Only superusers can create users.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if user already exists in this tenant
    user = crud.user.get_by_email(
        db, email=user_in.email, tenant_id=current_user.tenant_id
    )
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the tenant.",
        )

    # Create user
    user = crud.user.create(db, obj_in=user_in, tenant_id=current_user.tenant_id)
    
    # Assign roles if provided
    if user_in.role_ids:
        for role_id in user_in.role_ids:
            role = crud.role.get(db, id=role_id)
            if role and (role.tenant_id == current_user.tenant_id or role.tenant_id is None):
                crud.role.assign_to_user(db, role_id=role_id, user_id=user.id)
    
    # Refresh to get roles
    db.refresh(user)
    return user


@router.get("/me", response_model=schemas.UserWithRoles)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.UserWithRoles)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if user belongs to the same tenant
    if user.tenant_id != current_user.tenant_id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.put("/{user_id}", response_model=schemas.UserWithRoles)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdateWithRoles,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update user.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if user belongs to the same tenant
    if user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify users from other tenants",
        )
    
    # Update roles if provided
    if user_in.role_ids is not None:
        # Remove all current roles
        user.roles = []
        db.flush()
        
        # Assign new roles
        for role_id in user_in.role_ids:
            role = crud.role.get(db, id=role_id)
            if role and (role.tenant_id == current_user.tenant_id or role.tenant_id is None):
                crud.role.assign_to_user(db, role_id=role_id, user_id=user.id)
    
    # Update other fields
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete user.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if user belongs to the same tenant
    if user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete users from other tenants",
        )
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
    
    crud.user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}
