"""
API v1 router configuration.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin_example,
    auth,
    health,
    management,
    management_auth,
    notifications,
    password_reset,
    pdf_templates,
    permissions,
    request_analytics,
    roles,
    services,
    tenants,
    users,
    wathq_external,
    wathq_logs,
    wathq_offline,
    ws_notifications,
)
from app.wathq.commercial_registration import endpoints as wathq_cr
from app.wathq.company_contract import endpoints as wathq_cc
from app.wathq.attorney import endpoints as wathq_attorney
from app.wathq.real_estate import endpoints as wathq_real_estate
from app.wathq.spl_national_address import endpoints as wathq_spl_address
from app.wathq.employee import endpoints as wathq_employee

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(
    permissions.router, prefix="/permissions", tags=["permissions"]
)
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
# WebSocket endpoint for real-time notifications
api_router.include_router(ws_notifications.router, tags=["websocket"])
api_router.include_router(
    management_auth.router, prefix="/management/auth", tags=["management-auth"]
)
api_router.include_router(
    password_reset.router, prefix="/management/password", tags=["password-reset"]
)
api_router.include_router(management.router, prefix="/management", tags=["management"])
api_router.include_router(
    admin_example.router, prefix="/admin", tags=["admin-examples"]
)
api_router.include_router(wathq_cr.router, prefix="/wathq/commercial-registration", tags=["wathq-commercial-registration"])
api_router.include_router(wathq_cc.router, prefix="/wathq/company-contract", tags=["wathq-company-contract"])
api_router.include_router(wathq_attorney.router, prefix="/wathq/attorney", tags=["wathq-attorney"])
api_router.include_router(wathq_real_estate.router, prefix="/wathq/real-estate", tags=["wathq-real-estate"])
api_router.include_router(wathq_spl_address.router, prefix="/wathq/spl-national-address", tags=["wathq-spl-national-address"])
api_router.include_router(wathq_employee.router, prefix="/wathq/employee", tags=["wathq-employee"])
api_router.include_router(wathq_logs.router, prefix="/wathq/logs", tags=["wathq-logs"])
api_router.include_router(wathq_offline.router, prefix="/wathq/offline", tags=["wathq-offline"])

# WATHQ External API endpoints - separate for tenant and management users
api_router.include_router(
    wathq_external.tenant_router, 
    prefix="/wathq/external", 
    tags=["wathq-external-tenant"]
)
api_router.include_router(
    wathq_external.management_router, 
    prefix="/management/wathq/external", 
    tags=["wathq-external-management"]
)

# Request Analytics endpoints - for management users only
api_router.include_router(
    request_analytics.router,
    prefix="/management/analytics",
    tags=["request-analytics"]
)

# PDF Templates endpoints - for management users only
api_router.include_router(
    pdf_templates.router,
    prefix="/pdf-templates",
    tags=["pdf-templates"]
)
