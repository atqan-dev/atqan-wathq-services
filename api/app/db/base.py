"""
Base database configuration.
"""

# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.tenant import Tenant  # noqa
from app.models.permission import Permission, Role  # noqa
from app.models.management_user import ManagementUser  # noqa
from app.models.management_user_profile import ManagementUserProfile  # noqa
from app.models.service import Service, TenantService  # noqa
from app.models.notification import Notification  # noqa
from app.models.api_request_counter import ApiRequestCounter, ApiRequestSummary  # noqa
from app.models.pdf_template import PdfTemplate, PdfTemplateVersion, GeneratedPdf  # noqa
from app.models.wathq_call_log import WathqCallLog  # noqa
from app.models.wathq_offline_data import WathqOfflineData  # noqa
from app.models.wathq_commercial_registration import CommercialRegistration  # noqa
from app.models.wathq_capital_info import CapitalInfo  # noqa
from app.models.wathq_cr_entity_character import CREntityCharacter  # noqa
from app.models.wathq_cr_activity import CRActivity  # noqa
from app.models.wathq_cr_stock import CRStock  # noqa
from app.models.wathq_cr_estore import CREstore  # noqa
from app.models.wathq_cr_estore_activity import CREstoreActivity  # noqa
from app.models.wathq_cr_party import CRParty  # noqa
from app.models.wathq_cr_party_partnership import CRPartyPartnership  # noqa
from app.models.wathq_cr_manager import CRManager  # noqa
from app.models.wathq_cr_manager_position import CRManagerPosition  # noqa
from app.models.wathq_cr_liquidator import CRLiquidator  # noqa
from app.models.wathq_cr_liquidator_position import CRLiquidatorPosition  # noqa
