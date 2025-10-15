"""
CRUD operations for Permission model.
"""


from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Permission | None:
        """Get permission by name."""
        return db.query(Permission).filter(Permission.name == name).first()

    def get_by_resource_action(
        self, db: Session, *, resource: str, action: str, scope: str = "tenant"
    ) -> Permission | None:
        """Get permission by resource, action, and scope."""
        return (
            db.query(Permission)
            .filter(
                Permission.resource == resource,
                Permission.action == action,
                Permission.scope == scope,
            )
            .first()
        )

    def get_active_permissions(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Permission]:
        """Get active permissions."""
        return (
            db.query(Permission)
            .filter(Permission.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_permissions_by_scope(
        self, db: Session, *, scope: str, skip: int = 0, limit: int = 100
    ) -> list[Permission]:
        """Get permissions by scope (tenant or system)."""
        return (
            db.query(Permission)
            .filter(Permission.scope == scope, Permission.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_default_permissions(self, db: Session) -> list[Permission]:
        """Create default permissions for the system."""
        default_permissions = [
            # User management
            {
                "name": "create_user",
                "resource": "user",
                "action": "create",
                "scope": "tenant",
                "description": "Create new users",
            },
            {
                "name": "read_user",
                "resource": "user",
                "action": "read",
                "scope": "tenant",
                "description": "View user information",
            },
            {
                "name": "update_user",
                "resource": "user",
                "action": "update",
                "scope": "tenant",
                "description": "Update user information",
            },
            {
                "name": "delete_user",
                "resource": "user",
                "action": "delete",
                "scope": "tenant",
                "description": "Delete users",
            },
            # Role management
            {
                "name": "create_role",
                "resource": "role",
                "action": "create",
                "scope": "tenant",
                "description": "Create new roles",
            },
            {
                "name": "read_role",
                "resource": "role",
                "action": "read",
                "scope": "tenant",
                "description": "View role information",
            },
            {
                "name": "update_role",
                "resource": "role",
                "action": "update",
                "scope": "tenant",
                "description": "Update role information",
            },
            {
                "name": "delete_role",
                "resource": "role",
                "action": "delete",
                "scope": "tenant",
                "description": "Delete roles",
            },
            {
                "name": "assign_role",
                "resource": "role",
                "action": "assign",
                "scope": "tenant",
                "description": "Assign roles to users",
            },
            # Tenant management (system level)
            {
                "name": "create_tenant",
                "resource": "tenant",
                "action": "create",
                "scope": "system",
                "description": "Create new tenants",
            },
            {
                "name": "read_tenant",
                "resource": "tenant",
                "action": "read",
                "scope": "system",
                "description": "View tenant information",
            },
            {
                "name": "update_tenant",
                "resource": "tenant",
                "action": "update",
                "scope": "system",
                "description": "Update tenant information",
            },
            {
                "name": "delete_tenant",
                "resource": "tenant",
                "action": "delete",
                "scope": "system",
                "description": "Delete tenants",
            },
            # Reports and analytics
            {
                "name": "read_reports",
                "resource": "report",
                "action": "read",
                "scope": "tenant",
                "description": "View reports and analytics",
            },
            {
                "name": "export_data",
                "resource": "data",
                "action": "export",
                "scope": "tenant",
                "description": "Export tenant data",
            },
        ]

        created_permissions = []
        for perm_data in default_permissions:
            existing = self.get_by_name(db, name=perm_data["name"])
            if not existing:
                permission = Permission(**perm_data)
                db.add(permission)
                created_permissions.append(permission)

        db.commit()
        return created_permissions


permission = CRUDPermission(Permission)
