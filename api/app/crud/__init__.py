"""
CRUD operations package.
"""

from .crud_management_user import management_user
from .crud_management_user_profile import management_user_profile
from .crud_notification import notification
from .crud_permission import permission
from .crud_role import role
from .crud_service import service, tenant_service
from .crud_tenant import tenant
from .crud_user import user
from .crud_wathq_call_log import wathq_call_log
from .crud_wathq_offline_data import wathq_offline_data
from .crud_cr_request import cr_request
from .crud_pdf_template import (
    generated_pdf,
    pdf_template,
    pdf_template_version,
)
from .crud_wathq_commercial_registration import (
    commercial_registration,
    capital_info,
    cr_entity_character,
    cr_activity,
    cr_stock,
    cr_estore,
    cr_estore_activity,
    cr_party,
    cr_party_partnership,
    cr_manager,
    cr_manager_position,
    cr_liquidator,
    cr_liquidator_position,
)

__all__ = [
    "user",
    "tenant",
    "permission",
    "role",
    "management_user",
    "service",
    "tenant_service",
    "notification",
    "management_user_profile",
    "wathq_call_log",
    "wathq_offline_data",
    "cr_request",
    "pdf_template",
    "pdf_template_version",
    "generated_pdf",
    "commercial_registration",
    "capital_info",
    "cr_entity_character",
    "cr_activity",
    "cr_stock",
    "cr_estore",
    "cr_estore_activity",
    "cr_party",
    "cr_party_partnership",
    "cr_manager",
    "cr_manager_position",
    "cr_liquidator",
    "cr_liquidator_position",
]
