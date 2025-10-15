"""
Role management endpoints.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.permissions import require_manage_roles_permission

router = APIRouter()


@router.get("/", response_model=list[schemas.Role])
def read_roles(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve roles for current tenant.
    """
    roles = crud.role.get_roles_by_tenant(
        db, tenant_id=current_user.tenant_id, skip=skip, limit=limit
    )
    return roles


@router.post("/", response_model=schemas.Role)
def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role_in: schemas.RoleCreate,
    current_user: models.User = Depends(require_manage_roles_permission),
) -> Any:
    """
    Create new role in current tenant.
    """
    # Check if role already exists in this tenant
    existing_role = crud.role.get_by_name_and_tenant(
        db, name=role_in.name, tenant_id=current_user.tenant_id
    )
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists in the tenant",
        )

    role = crud.role.create_with_permissions(
        db, obj_in=role_in, tenant_id=current_user.tenant_id
    )
    return role


@router.get("/{role_id}", response_model=schemas.Role)
def read_role(
    role_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get role by ID.
    """
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Check if role belongs to current tenant or is a system role
    if role.tenant_id and role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return role


@router.put("/{role_id}", response_model=schemas.Role)
def update_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: int,
    role_in: schemas.RoleUpdate,
    current_user: models.User = Depends(require_manage_roles_permission),
) -> Any:
    """
    Update role.
    """
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Check if role belongs to current tenant
    if role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify roles from other tenants",
        )

    # Update permissions if provided
    if role_in.permission_ids is not None:
        role = crud.role.update_permissions(
            db, role=role, permission_ids=role_in.permission_ids
        )

    # Update other fields
    role_data = role_in.dict(exclude={"permission_ids"}, exclude_unset=True)
    role = crud.role.update(db, db_obj=role, obj_in=role_data)
    return role


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_manage_roles_permission),
) -> Any:
    """
    Delete role.
    """
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Check if role belongs to current tenant
    if role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete roles from other tenants",
        )

    # Check if it's a default role
    if role.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default role",
        )

    crud.role.remove(db, id=role_id)
    return {"message": "Role deleted successfully"}


@router.post("/{role_id}/assign/{user_id}")
def assign_role_to_user(
    role_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_manage_roles_permission),
) -> Any:
    """
    Assign role to user.
    """
    # Check if role exists and belongs to current tenant
    role = crud.role.get(db, id=role_id)
    if not role or role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Check if user exists and belongs to current tenant
    user = crud.user.get(db, id=user_id)
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    success = crud.role.assign_to_user(db, role_id=role_id, user_id=user_id)
    if success:
        return {"message": "Role assigned successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign role",
        )


@router.delete("/{role_id}/assign/{user_id}")
def remove_role_from_user(
    role_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_manage_roles_permission),
) -> Any:
    """
    Remove role from user.
    """
    # Check if role exists and belongs to current tenant
    role = crud.role.get(db, id=role_id)
    if not role or role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Check if user exists and belongs to current tenant
    user = crud.user.get(db, id=user_id)
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    success = crud.role.remove_from_user(db, role_id=role_id, user_id=user_id)
    if success:
        return {"message": "Role removed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove role",
        )


@router.post("/initialize-defaults", response_model=list[schemas.Role])
def initialize_default_roles(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_manage_roles_permission),
) -> Any:
    """
    Initialize default roles for current tenant.
    """
    roles = crud.role.create_default_roles(db, tenant_id=current_user.tenant_id)
    return roles
