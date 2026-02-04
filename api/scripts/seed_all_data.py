"""
Comprehensive seed script for Atqan WATHQ Services.

Seeds:
- Management Users (superusers: mahmoud-alattar, talal)
- Tenant: Tawthiq
- Tenant Users (admin, management roles)
- WATHQ Services
- Permissions and Roles
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session

from app.core.security import pwd_context
from app.db.session import SessionLocal
from app.models.management_user import ManagementUser
from app.models.permission import Permission, Role
from app.models.service import Service
from app.models.tenant import Tenant
from app.models.user import User


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_PASSWORD = "Admin@123456"
HASHED_PASSWORD = pwd_context.hash(DEFAULT_PASSWORD)


# =============================================================================
# Management Users (Cross-tenant superusers)
# =============================================================================

MANAGEMENT_USERS = [
    {
        "email": "mahmoud@atqan.sa",
        "first_name": "Mahmoud",
        "last_name": "Al-Attar",
        "name_ar": "محمود العطار",
        "is_super_admin": True,
        "is_active": True,
    },
    {
        "email": "talal@atqan.sa",
        "first_name": "Talal",
        "last_name": "Admin",
        "name_ar": "طلال",
        "is_super_admin": True,
        "is_active": True,
    },
]


# =============================================================================
# Tenants
# =============================================================================

TENANTS = [
    {
        "name": "Tawthiq",
        "name_ar": "توثيق",
        "slug": "tawthiq",
        "description": "Tawthiq - Document Verification and Notarization Services",
        "is_active": True,
        "max_users": 100,
    },
]


# =============================================================================
# WATHQ Services
# =============================================================================

WATHQ_SERVICES = [
    {
        "name": "Commercial Registration",
        "slug": "commercial-registration",
        "description": "WATHQ Commercial Registration Service - Verify business registration details",
        "category": "wathq",
        "price": 0.00,
        "requires_approval": True,
    },
    {
        "name": "Real Estate",
        "slug": "real-estate",
        "description": "WATHQ Real Estate Verification Service - Property ownership and details",
        "category": "wathq",
        "price": 0.00,
        "requires_approval": True,
    },
    {
        "name": "Employee Verification",
        "slug": "employee-verification",
        "description": "WATHQ Employee Verification Service - Verify employment status",
        "category": "wathq",
        "price": 0.00,
        "requires_approval": True,
    },
    {
        "name": "Company Contract",
        "slug": "company-contract",
        "description": "WATHQ Company Contract Service - Contract verification and management",
        "category": "wathq",
        "price": 0.00,
        "requires_approval": True,
    },
    {
        "name": "Attorney Services",
        "slug": "attorney-services",
        "description": "WATHQ Attorney Services - Legal verification and attorney information",
        "category": "wathq",
        "price": 0.00,
        "requires_approval": True,
    },
    {
        "name": "National Address",
        "slug": "national-address",
        "description": "WATHQ National Address Service - Address verification and validation",
        "category": "wathq",
        "price": 0.00,
        "requires_approval": True,
    },
]


# =============================================================================
# Permissions
# =============================================================================

PERMISSIONS = [
    # WATHQ Service permissions
    {"name": "use_commercial_registration", "description": "Use Commercial Registration Service", "resource": "wathq_service", "action": "use", "scope": "service", "service_slug": "commercial-registration"},
    {"name": "use_real_estate", "description": "Use Real Estate Service", "resource": "wathq_service", "action": "use", "scope": "service", "service_slug": "real-estate"},
    {"name": "use_employee_verification", "description": "Use Employee Verification Service", "resource": "wathq_service", "action": "use", "scope": "service", "service_slug": "employee-verification"},
    {"name": "use_company_contract", "description": "Use Company Contract Service", "resource": "wathq_service", "action": "use", "scope": "service", "service_slug": "company-contract"},
    {"name": "use_attorney_services", "description": "Use Attorney Services", "resource": "wathq_service", "action": "use", "scope": "service", "service_slug": "attorney-services"},
    {"name": "use_national_address", "description": "Use National Address Service", "resource": "wathq_service", "action": "use", "scope": "service", "service_slug": "national-address"},
    # Tenant management permissions
    {"name": "manage_tenant_services", "description": "Manage Tenant Services", "resource": "tenant_service", "action": "manage", "scope": "tenant", "service_slug": None},
    {"name": "approve_service_requests", "description": "Approve Service Requests", "resource": "tenant_service", "action": "approve", "scope": "tenant", "service_slug": None},
    {"name": "assign_user_services", "description": "Assign Services to Users", "resource": "user_service", "action": "assign", "scope": "tenant", "service_slug": None},
    {"name": "view_service_usage", "description": "View Service Usage Statistics", "resource": "tenant_service", "action": "read", "scope": "tenant", "service_slug": None},
    # User management permissions
    {"name": "manage_users", "description": "Create, update, delete users", "resource": "user", "action": "manage", "scope": "tenant", "service_slug": None},
    {"name": "view_users", "description": "View users in tenant", "resource": "user", "action": "read", "scope": "tenant", "service_slug": None},
    # Role management permissions
    {"name": "manage_roles", "description": "Create, update, delete roles", "resource": "role", "action": "manage", "scope": "tenant", "service_slug": None},
    {"name": "assign_roles", "description": "Assign roles to users", "resource": "role", "action": "assign", "scope": "tenant", "service_slug": None},
]


# =============================================================================
# Seed Functions
# =============================================================================

def seed_management_users(db: Session) -> list[ManagementUser]:
    """Seed management users (superusers)."""
    print("\n" + "=" * 60)
    print("Seeding Management Users...")
    print("=" * 60)
    
    created_users = []
    for user_data in MANAGEMENT_USERS:
        existing = db.query(ManagementUser).filter(
            ManagementUser.email == user_data["email"]
        ).first()
        
        if not existing:
            user = ManagementUser(
                **user_data,
                hashed_password=HASHED_PASSWORD,
            )
            db.add(user)
            db.flush()
            created_users.append(user)
            print(f"  ✓ Created: {user_data['first_name']} {user_data['last_name']} ({user_data['email']})")
        else:
            created_users.append(existing)
            print(f"  - Exists: {user_data['email']}")
    
    db.commit()
    return created_users


def seed_tenants(db: Session) -> list[Tenant]:
    """Seed tenants."""
    print("\n" + "=" * 60)
    print("Seeding Tenants...")
    print("=" * 60)
    
    created_tenants = []
    for tenant_data in TENANTS:
        existing = db.query(Tenant).filter(Tenant.slug == tenant_data["slug"]).first()
        
        if not existing:
            tenant = Tenant(**tenant_data)
            db.add(tenant)
            db.flush()
            created_tenants.append(tenant)
            print(f"  ✓ Created: {tenant_data['name']} (slug: {tenant_data['slug']})")
        else:
            created_tenants.append(existing)
            print(f"  - Exists: {tenant_data['name']}")
    
    db.commit()
    return created_tenants


def seed_services(db: Session) -> list[Service]:
    """Seed WATHQ services."""
    print("\n" + "=" * 60)
    print("Seeding WATHQ Services...")
    print("=" * 60)
    
    created_services = []
    for service_data in WATHQ_SERVICES:
        existing = db.query(Service).filter(Service.slug == service_data["slug"]).first()
        
        if not existing:
            service = Service(**service_data)
            db.add(service)
            db.flush()
            created_services.append(service)
            print(f"  ✓ Created: {service_data['name']}")
        else:
            created_services.append(existing)
            print(f"  - Exists: {service_data['name']}")
    
    db.commit()
    return created_services


def seed_permissions(db: Session) -> list[Permission]:
    """Seed permissions."""
    print("\n" + "=" * 60)
    print("Seeding Permissions...")
    print("=" * 60)
    
    created_permissions = []
    for perm_data in PERMISSIONS:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            db.flush()
            created_permissions.append(permission)
            print(f"  ✓ Created: {perm_data['name']}")
        else:
            created_permissions.append(existing)
            print(f"  - Exists: {perm_data['name']}")
    
    db.commit()
    return created_permissions


def seed_roles(db: Session, tenant: Tenant) -> dict[str, Role]:
    """Seed roles for a tenant."""
    print("\n" + "=" * 60)
    print(f"Seeding Roles for Tenant: {tenant.name}...")
    print("=" * 60)
    
    # Get all permissions
    all_permissions = db.query(Permission).all()
    service_permissions = [p for p in all_permissions if p.resource == "wathq_service"]
    management_permissions = [p for p in all_permissions if p.name in [
        "manage_tenant_services", "approve_service_requests", "assign_user_services",
        "view_service_usage", "manage_users", "view_users", "manage_roles", "assign_roles"
    ]]
    
    roles_config = [
        {
            "name": "Admin",
            "description": "Full administrative access to tenant",
            "permissions": all_permissions,
            "is_default": False,
        },
        {
            "name": "Manager",
            "description": "Manage services and users",
            "permissions": service_permissions + management_permissions,
            "is_default": False,
        },
        {
            "name": "User",
            "description": "Basic access to assigned services",
            "permissions": service_permissions,
            "is_default": True,
        },
    ]
    
    created_roles = {}
    for role_data in roles_config:
        existing = db.query(Role).filter(
            Role.name == role_data["name"],
            Role.tenant_id == tenant.id
        ).first()
        
        if not existing:
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                tenant_id=tenant.id,
                is_default=role_data["is_default"],
            )
            role.permissions = role_data["permissions"]
            db.add(role)
            db.flush()
            created_roles[role_data["name"]] = role
            print(f"  ✓ Created: {role_data['name']}")
        else:
            created_roles[role_data["name"]] = existing
            print(f"  - Exists: {role_data['name']}")
    
    db.commit()
    return created_roles


def seed_tenant_users(db: Session, tenant: Tenant, roles: dict[str, Role]) -> list[User]:
    """Seed users for a tenant."""
    print("\n" + "=" * 60)
    print(f"Seeding Users for Tenant: {tenant.name}...")
    print("=" * 60)
    
    users_config = [
        {
            "email": "admin@tawthiq.sa",
            "first_name": "Admin",
            "last_name": "Tawthiq",
            "name_ar": "مدير توثيق",
            "is_superuser": True,
            "role": "Admin",
        },
        {
            "email": "manager@tawthiq.sa",
            "first_name": "Manager",
            "last_name": "Tawthiq",
            "name_ar": "مشرف توثيق",
            "is_superuser": False,
            "role": "Manager",
        },
    ]
    
    created_users = []
    for user_data in users_config:
        role_name = user_data.pop("role")
        
        existing = db.query(User).filter(
            User.email == user_data["email"],
            User.tenant_id == tenant.id
        ).first()
        
        if not existing:
            user = User(
                **user_data,
                hashed_password=HASHED_PASSWORD,
                tenant_id=tenant.id,
                is_active=True,
            )
            if role_name in roles:
                user.roles = [roles[role_name]]
            db.add(user)
            db.flush()
            created_users.append(user)
            print(f"  ✓ Created: {user_data['first_name']} {user_data['last_name']} ({user_data['email']}) - Role: {role_name}")
        else:
            created_users.append(existing)
            print(f"  - Exists: {user_data['email']}")
    
    db.commit()
    return created_users


# =============================================================================
# Main
# =============================================================================

def main():
    """Main function to seed all data."""
    print("\n" + "=" * 60)
    print("  ATQAN WATHQ SERVICES - DATABASE SEEDING")
    print("=" * 60)
    print(f"\nDefault password for all users: {DEFAULT_PASSWORD}")
    
    db = SessionLocal()
    try:
        # 1. Seed Management Users (superusers)
        management_users = seed_management_users(db)
        
        # 2. Seed Tenants
        tenants = seed_tenants(db)
        
        # 3. Seed WATHQ Services
        services = seed_services(db)
        
        # 4. Seed Permissions
        permissions = seed_permissions(db)
        
        # 5. Seed Roles and Users for each tenant
        for tenant in tenants:
            roles = seed_roles(db, tenant)
            users = seed_tenant_users(db, tenant, roles)
        
        print("\n" + "=" * 60)
        print("  SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Management Users: {len(management_users)}")
        print(f"  - Tenants: {len(tenants)}")
        print(f"  - WATHQ Services: {len(services)}")
        print(f"  - Permissions: {len(permissions)}")
        print("\nLogin Credentials:")
        print("  Management Users (Superusers):")
        for user in MANAGEMENT_USERS:
            print(f"    - {user['email']} / {DEFAULT_PASSWORD}")
        print("  Tenant Users (Tawthiq):")
        print(f"    - admin@tawthiq.sa / {DEFAULT_PASSWORD} (Admin)")
        print(f"    - manager@tawthiq.sa / {DEFAULT_PASSWORD} (Manager)")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
