"""
Base database configuration.
"""

# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.management_user import ManagementUser
from app.models.management_user_profile import ManagementUserProfile
from app.models.notification import Notification
from app.models.permission import Permission, Role
from app.models.service import Service, TenantService
from app.models.tenant import Tenant
from app.models.user import User
from app.models.wathq_call_log import WathqCallLog
from app.models.wathq_offline_data import WathqOfflineData
