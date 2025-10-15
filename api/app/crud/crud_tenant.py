"""
CRUD operations for Tenant model.
"""


from sqlalchemy.orm import Session
from sqlalchemy import func
import logging


from app.crud.base import CRUDBase
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantUpdate

logger = logging.getLogger(__name__)


class CRUDTenant(CRUDBase[Tenant, TenantCreate, TenantUpdate]):
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Tenant]:
        """Get multiple tenants with users count."""
        # Subquery to count users per tenant
        user_count_subquery = (
            db.query(
                User.tenant_id,
                func.count(User.id).label("users_count")
            )
            .group_by(User.tenant_id)
            .subquery()
        )
        
        # Query tenants with users count
        tenants = (
            db.query(Tenant, user_count_subquery.c.users_count)
            .outerjoin(
                user_count_subquery,
                Tenant.id == user_count_subquery.c.tenant_id
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Attach users_count to each tenant object
        result = []
        for tenant, users_count in tenants:
            tenant.users_count = users_count or 0
            result.append(tenant)
        
        return result
    
    def get_by_slug(self, db: Session, *, slug: str) -> Tenant | None:
        """Get tenant by slug."""
        return db.query(Tenant).filter(Tenant.slug == slug).first()



    def create(self, db: Session, *, obj_in: TenantCreate) -> Tenant:
        """Create new tenant with default roles."""
        try:
            logger.info(f"Creating tenant with slug: {obj_in.slug}")

            # Create tenant record
            db_obj = Tenant(
                name=obj_in.name,
                slug=obj_in.slug,
                name_ar=obj_in.name_ar,
                logo=obj_in.logo,
                description=obj_in.description,
                is_active=True,
                max_users=obj_in.max_users or 100,
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Tenant record created with ID: {db_obj.id}")

            # Create default roles for the tenant
            try:
                from app.crud.crud_role import role
                logger.info(f"Creating default roles for tenant ID: {db_obj.id}")
                role.create_default_roles(db, tenant_id=db_obj.id)
                logger.info(f"Default roles created for tenant ID: {db_obj.id}")
            except Exception as e:
                logger.error(f"Failed to create default roles: {str(e)}", exc_info=True)
                # Don't rollback tenant creation for role creation failure
                pass

            return db_obj
        except Exception as e:
            logger.error(f"Failed to create tenant: {str(e)}", exc_info=True)
            raise

    def get_active_tenants(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Tenant]:
        """Get active tenants."""
        return (
            db.query(Tenant)
            .filter(Tenant.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def deactivate(self, db: Session, *, tenant_id: int) -> Tenant | None:
        """Deactivate tenant (soft delete)."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            tenant.is_active = False
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        return tenant

    def activate(self, db: Session, *, tenant_id: int) -> Tenant | None:
        """Activate tenant."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            tenant.is_active = True
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        return tenant


tenant = CRUDTenant(Tenant)
