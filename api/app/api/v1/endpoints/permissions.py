"""
Permission management endpoints.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.permissions import (
    require_tenant_admin_permission,
)

router = APIRouter()


@router.get("/", response_model=list[schemas.Permission])
def read_permissions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve permissions. All authenticated users can view permissions.
    """
    permissions = crud.permission.get_active_permissions(db, skip=skip, limit=limit)
    return permissions


@router.post("/", response_model=schemas.Permission)
def create_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_in: schemas.PermissionCreate,
    current_user: models.User = Depends(require_tenant_admin_permission),
) -> Any:
    """
    Create new permission. Only system administrators can create permissions.
    """
    # Check if permission already exists
    existing_permission = crud.permission.get_by_name(db, name=permission_in.name)
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission with this name already exists",
        )

    permission = crud.permission.create(db, obj_in=permission_in)
    return permission


@router.get("/scope/{scope}", response_model=list[schemas.Permission])
def read_permissions_by_scope(
    scope: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve permissions by scope (tenant or system).
    """
    if scope not in ["tenant", "system"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scope must be 'tenant' or 'system'",
        )

    permissions = crud.permission.get_permissions_by_scope(
        db, scope=scope, skip=skip, limit=limit
    )
    return permissions


@router.post("/initialize-defaults", response_model=list[schemas.Permission])
def initialize_default_permissions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_tenant_admin_permission),
) -> Any:
    """
    Initialize default permissions. Only system administrators can do this.
    """
    permissions = crud.permission.create_default_permissions(db)
    return permissions
