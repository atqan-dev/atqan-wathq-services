"""
CRUD operations for Role model.
"""


from sqlalchemy.orm import Session
import logging

from app.crud.base import CRUDBase
from app.models.permission import Permission, Role
from app.schemas.permission import RoleCreate, RoleUpdate

logger = logging.getLogger(__name__)


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def get_by_name_and_tenant(
        self, db: Session, *, name: str, tenant_id: int | None = None
    ) -> Role | None:
        """Get role by name and tenant."""
        query = db.query(Role).filter(Role.name == name)
        if tenant_id:
            query = query.filter(Role.tenant_id == tenant_id)
        else:
            query = query.filter(Role.tenant_id.is_(None))
        return query.first()

    def get_roles_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> list[Role]:
        """Get roles for a specific tenant."""
        return (
            db.query(Role)
            .filter(Role.tenant_id == tenant_id, Role.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_system_roles(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Role]:
        """Get system-wide roles."""
        return (
            db.query(Role)
            .filter(Role.tenant_id.is_(None), Role.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_default_role_for_tenant(
        self, db: Session, *, tenant_id: int
    ) -> Role | None:
        """Get the default role for a tenant."""
        return (
            db.query(Role)
            .filter(
                Role.tenant_id == tenant_id,
                Role.is_default == True,
                Role.is_active == True,
            )
            .first()
        )

    def create_with_permissions(
        self, db: Session, *, obj_in: RoleCreate, tenant_id: int | None = None
    ) -> Role:
        """Create role with associated permissions."""
        try:
            # Create the role
            role_data = obj_in.dict(exclude={"permission_ids"})
            role_data["tenant_id"] = tenant_id
            role = Role(**role_data)
            db.add(role)
            db.flush()  # To get the role ID

            # Add permissions if provided
            if obj_in.permission_ids:
                permissions = (
                    db.query(Permission)
                    .filter(Permission.id.in_(obj_in.permission_ids))
                    .all()
                )
                role.permissions = permissions

            db.commit()
            db.refresh(role)
            return role
        except Exception as e:
            logger.error(f"Failed to create role with permissions: {str(e)}", exc_info=True)
            db.rollback()
            raise

    def update_permissions(
        self, db: Session, *, role: Role, permission_ids: list[int]
    ) -> Role:
        """Update role permissions."""
        permissions = (
            db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        )
        role.permissions = permissions
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    def assign_to_user(self, db: Session, *, role_id: int, user_id: int) -> bool:
        """Assign role to user."""
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.id == role_id).first()

        if user and role:
            if role not in user.roles:
                user.roles.append(role)
                db.add(user)
                db.commit()
            return True
        return False

    def remove_from_user(self, db: Session, *, role_id: int, user_id: int) -> bool:
        """Remove role from user."""
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.id == role_id).first()

        if user and role and role in user.roles:
            user.roles.remove(role)
            db.add(user)
            db.commit()
            return True
        return False

    def create_default_roles(self, db: Session, *, tenant_id: int) -> list[Role]:
        """Create default roles for a tenant."""
        try:
            logger.info(f"Creating default roles for tenant ID: {tenant_id}")
            from app.crud.crud_permission import permission

            default_roles = [
                {
                    "name": "admin",
                    "description": "Full administrative access to the tenant",
                    "is_default": False,
                    "permissions": [
                        "create_user",
                        "read_user",
                        "update_user",
                        "delete_user",
                        "create_role",
                        "read_role",
                        "update_role",
                        "delete_role",
                        "assign_role",
                        "read_reports",
                        "export_data",
                    ],
                },
                {
                    "name": "manager",
                    "description": "Management access with user and role management",
                    "is_default": False,
                    "permissions": [
                        "create_user",
                        "read_user",
                        "update_user",
                        "read_role",
                        "assign_role",
                        "read_reports",
                    ],
                },
                {
                    "name": "member",
                    "description": "Basic member access",
                    "is_default": True,
                    "permissions": ["read_user", "read_role"],
                },
            ]

            created_roles = []
            for role_data in default_roles:
                existing = self.get_by_name_and_tenant(
                    db, name=role_data["name"], tenant_id=tenant_id
                )
                if not existing:
                    # Get permission IDs
                    permission_names = role_data.pop("permissions", [])
                    permission_ids = []
                    for perm_name in permission_names:
                        perm = permission.get_by_name(db, name=perm_name)
                        if perm:
                            permission_ids.append(perm.id)

                    # Create role with permissions
                    logger.info(f"Creating role {role_data['name']} for tenant {tenant_id}")
                    role_create = RoleCreate(**role_data, permission_ids=permission_ids)
                    role = self.create_with_permissions(
                        db, obj_in=role_create, tenant_id=tenant_id
                    )
                    created_roles.append(role)
                    logger.info(f"Created role {role.name} with ID {role.id}")

            logger.info(f"Finished creating default roles for tenant ID: {tenant_id}")
            return created_roles
        except Exception as e:
            logger.error(f"Failed to create default roles for tenant {tenant_id}: {str(e)}", exc_info=True)
            raise


role = CRUDRole(Role)
