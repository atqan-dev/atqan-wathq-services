"""
Permission checking utilities and dependencies.
"""


from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User


def get_user_permissions(db: Session, user: User) -> list[str]:
    """Get all permission names for a user."""
    permissions = set()

    # Get permissions from user's roles
    for role in user.roles:
        for permission in role.permissions:
            if permission.is_active:
                permissions.add(permission.name)

    return list(permissions)


def user_has_permission(db: Session, user: User, permission_name: str) -> bool:
    """Check if user has a specific permission."""
    if user.is_superuser:
        return True

    user_permissions = get_user_permissions(db, user)
    return permission_name in user_permissions


def user_has_any_permission(
    db: Session, user: User, permission_names: list[str]
) -> bool:
    """Check if user has any of the specified permissions."""
    if user.is_superuser:
        return True

    user_permissions = get_user_permissions(db, user)
    return any(perm in user_permissions for perm in permission_names)


def user_has_all_permissions(
    db: Session, user: User, permission_names: list[str]
) -> bool:
    """Check if user has all of the specified permissions."""
    if user.is_superuser:
        return True

    user_permissions = get_user_permissions(db, user)
    return all(perm in user_permissions for perm in permission_names)


class PermissionChecker:
    """Dependency class for checking permissions."""

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not user_has_permission(db, current_user, self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{self.required_permission}' required",
            )
        return current_user


class AnyPermissionChecker:
    """Dependency class for checking if user has any of the specified permissions."""

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not user_has_any_permission(db, current_user, self.required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(self.required_permissions)}",
            )
        return current_user


class AllPermissionsChecker:
    """Dependency class for checking if user has all of the specified permissions."""

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not user_has_all_permissions(db, current_user, self.required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All of these permissions required: {', '.join(self.required_permissions)}",
            )
        return current_user


# Common permission dependency functions
def require_create_user_permission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Require 'create_user' permission."""
    if not user_has_permission(db, current_user, "create_user"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission 'create_user' required",
        )
    return current_user


def require_manage_roles_permission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Require role management permissions."""
    required_permissions = ["create_role", "update_role", "assign_role"]
    if not user_has_any_permission(db, current_user, required_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permissions required",
        )
    return current_user


def require_tenant_admin_permission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Require tenant administration permissions."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System administrator privileges required",
        )
    return current_user


def require_permission(user: User, permission_name: str, db: Session = None) -> None:
    """Check if user has required permission and raise exception if not."""
    if user.is_superuser:
        return
    
    # Simple permission check without database query for now
    # In production, you might want to check against user.roles
    user_permissions = []
    for role in user.roles:
        for permission in role.permissions:
            if permission.is_active:
                user_permissions.append(permission.name)
    
    if permission_name not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission_name}' required",
        )
