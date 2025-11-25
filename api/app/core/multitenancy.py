"""
Multitenancy utilities and middleware for tenant identification using single schema with tenant_id.
"""

import logging
from contextvars import ContextVar

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


class TenantContext:
    """
    Context object to store current tenant information.
    """

    def __init__(self):
        self.tenant_id: int | None = None
        self.tenant_slug: str | None = None


# Use ContextVar for thread-safe tenant context
tenant_context: ContextVar[TenantContext] = ContextVar('tenant_context', default=TenantContext())


def get_tenant_from_request(request: Request) -> str | None:
    """
    Extract tenant identifier from request.
    Supports multiple identification methods:
    1. Subdomain (tenant.example.com)
    2. X-Tenant-ID header
    3. tenant query parameter
    """
    # Method 1: Check X-Tenant-ID header
    tenant_header = request.headers.get("X-Tenant-ID")
    if tenant_header:
        return tenant_header.lower()

    # Method 2: Check subdomain
    host = request.headers.get("host", "")
    if host and "." in host:
        subdomain = host.split(".")[0]
        # Skip common subdomains
        if subdomain not in ["www", "api", "admin"]:
            return subdomain.lower()

    # Method 3: Check query parameter
    tenant_param = request.query_params.get("tenant")
    if tenant_param:
        return tenant_param.lower()

    return "default"  # Default tenant slug


def get_current_tenant() -> TenantContext:
    """
    Get current tenant context.
    """
    return tenant_context.get()


def set_current_tenant(tenant_id: int, tenant_slug: str) -> None:
    """
    Set current tenant context.
    """
    context = TenantContext()
    context.tenant_id = tenant_id
    context.tenant_slug = tenant_slug
    tenant_context.set(context)


def get_tenant_by_slug(db: Session, slug: str):
    """
    Get tenant by slug from database.
    """
    from app.models.tenant import Tenant
    return db.query(Tenant).filter(Tenant.slug == slug, Tenant.is_active == True).first()


def ensure_tenant_exists(db: Session, slug: str) -> int:
    """
    Ensure tenant exists and return tenant_id.
    Creates a default tenant if none exists.
    """
    from app.models.tenant import Tenant
    
    tenant = get_tenant_by_slug(db, slug)
    if not tenant:
        # Create default tenant if it doesn't exist
        tenant = Tenant(
            name=slug.title(),
            slug=slug,
            description=f"Auto-created tenant for {slug}",
            is_active=True
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        logger.info(f"Created new tenant: {slug} with ID: {tenant.id}")
    
    return tenant.id


async def tenant_identification_middleware(request: Request, call_next):
    """
    Middleware to identify and set tenant context for each request.
    """
    # Skip tenant identification for certain paths
    skip_paths = ["/docs", "/openapi.json", "/redoc", "/health", "/api/v1/management"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        response = await call_next(request)
        return response

    # Get tenant identifier
    tenant_slug = get_tenant_from_request(request)

    if tenant_slug:
        # Get database session to look up tenant
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            tenant_id = ensure_tenant_exists(db, tenant_slug)
            set_current_tenant(tenant_id, tenant_slug)
            logger.debug(f"Set tenant context: {tenant_slug} (ID: {tenant_id})")
        except Exception as e:
            logger.error(f"Failed to set tenant context for {tenant_slug}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Tenant initialization failed",
            )
        finally:
            db.close()
    else:
        # Default to tenant_id = 1 for requests without tenant identification
        set_current_tenant(1, "default")

    response = await call_next(request)
    return response
