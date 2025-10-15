"""
Pydantic schemas package.
"""

from .management_user import (
    ManagementUser,
    ManagementUserCreate,
    ManagementUserInDB,
    ManagementUserUpdate,
)
from .management_user_profile import (
    ManagementUserProfile,
    ManagementUserProfileCreate,
    ManagementUserProfileInDB,
    ManagementUserProfileUpdate,
    AvatarUpdate,
)
from .notification import (
    Notification,
    NotificationCreate,
    NotificationUpdate,
    NotificationMarkAsRead,
    NotificationStats,
    NotificationBulkCreate,
    NotificationFilter,
)
from .permission import (
    Permission,
    PermissionCreate,
    PermissionUpdate,
    Role,
    RoleCreate,
    RoleUpdate,
    UserRoleAssignment,
)
from .service import (
    Service,
    ServiceCreate,
    ServiceUpdate,
    TenantService,
    TenantServiceCreate,
    TenantServiceUpdate,
    ServiceListResponse,
    TenantServiceListResponse,
    UserAuthorizedServicesResponse,
    TenantServiceRequest,
    TenantServiceApproval,
    UserServiceAssignment,
    ManagementServicesResponse,
)
from .tenant import Tenant, TenantCreate, TenantInDB, TenantUpdate
from .token import Token
from .user import TokenPayload, User, UserCreate, UserInDB, UserUpdate
from .wathq_call_log import (
    WathqCallLog,
    WathqCallLogCreate,
    WathqCallLogUpdate,
    ServiceUsageStats,
    TenantUsageStats,
)
from .wathq_offline_data import (
    WathqOfflineData,
    WathqOfflineDataCreate,
    WathqOfflineDataUpdate,
)

__all__ = [
    "User",
    "UserCreate",
    "UserInDB",
    "UserUpdate",
    "TokenPayload",
    "Tenant",
    "TenantCreate",
    "TenantInDB",
    "TenantUpdate",
    "Token",
    "Permission",
    "PermissionCreate",
    "PermissionUpdate",
    "Role",
    "RoleCreate",
    "RoleUpdate",
    "UserRoleAssignment",
    "ManagementUser",
    "ManagementUserCreate",
    "ManagementUserInDB",
    "ManagementUserUpdate",
    "Notification",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationMarkAsRead",
    "NotificationStats",
    "NotificationBulkCreate",
    "NotificationFilter",
    "Service",
    "ServiceCreate",
    "ServiceUpdate",
    "TenantService",
    "TenantServiceCreate",
    "TenantServiceUpdate",
    "ServiceListResponse",
    "TenantServiceListResponse",
    "UserAuthorizedServicesResponse",
    "TenantServiceRequest",
    "TenantServiceApproval",
    "UserServiceAssignment",
    "WathqCallLog",
    "WathqCallLogCreate",
    "WathqCallLogUpdate",
    "ServiceUsageStats",
    "TenantUsageStats",
    "WathqOfflineData",
    "WathqOfflineDataCreate",
    "WathqOfflineDataUpdate",
    "ManagementUserProfile",
    "ManagementUserProfileCreate",
    "ManagementUserProfileInDB",
    "ManagementUserProfileUpdate",
    "AvatarUpdate",
]
