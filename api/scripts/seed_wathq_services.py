"""
Script to seed WATHQ services and permissions.
"""
import sys
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent.parent  # Go up one level from scripts/ to backend/
sys.path.insert(0, str(current_dir))

# Also add the current directory as fallback
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
import uuid
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.service import Service
from app.models.permission import Permission
from app.models.permission import Role


def seed_wathq_services(db: Session):
    """Seed WATHQ services."""
    
    services_data = [
        {
            "name": "Commercial Registration",
            "slug": "commercial-registration",
            "description": "WATHQ Commercial Registration Service - Verify business registration details",
            "category": "wathq",
            "price": 0.00,
            "requires_approval": True
        },
        {
            "name": "Real Estate",
            "slug": "real-estate",
            "description": "WATHQ Real Estate Verification Service - Property ownership and details",
            "category": "wathq",
            "price": 0.00,
            "requires_approval": True
        },
        {
            "name": "Employee Verification",
            "slug": "employee-verification",
            "description": "WATHQ Employee Verification Service - Verify employment status",
            "category": "wathq",
            "price": 0.00,
            "requires_approval": True
        },
        {
            "name": "Company Contract",
            "slug": "company-contract",
            "description": "WATHQ Company Contract Service - Contract verification and management",
            "category": "wathq",
            "price": 0.00,
            "requires_approval": True
        },
        {
            "name": "Attorney Services",
            "slug": "attorney-services",
            "description": "WATHQ Attorney Services - Legal verification and attorney information",
            "category": "wathq",
            "price": 0.00,
            "requires_approval": True
        },
        {
            "name": "National Address",
            "slug": "national-address",
            "description": "WATHQ National Address Service - Address verification and validation",
            "category": "wathq",
            "price": 0.00,
            "requires_approval": True
        }
    ]
    
    print("Seeding WATHQ services...")
    for service_data in services_data:
        existing = db.query(Service).filter(Service.slug == service_data["slug"]).first()
        if not existing:
            service = Service(
                id=uuid.uuid4(),
                **service_data
            )
            db.add(service)
            print(f"Created service: {service_data['name']}")
        else:
            print(f"Service already exists: {service_data['name']}")
    
    db.commit()


def seed_wathq_permissions(db: Session):
    """Seed WATHQ-specific permissions."""
    
    permissions_data = [
        # Service-specific permissions
        {
            "name": "use_commercial_registration",
            "description": "Use Commercial Registration Service",
            "resource": "wathq_service",
            "action": "use",
            "scope": "service",
            "service_slug": "commercial-registration"
        },
        {
            "name": "use_real_estate",
            "description": "Use Real Estate Service",
            "resource": "wathq_service",
            "action": "use",
            "scope": "service",
            "service_slug": "real-estate"
        },
        {
            "name": "use_employee_verification",
            "description": "Use Employee Verification Service",
            "resource": "wathq_service",
            "action": "use",
            "scope": "service",
            "service_slug": "employee-verification"
        },
        {
            "name": "use_company_contract",
            "description": "Use Company Contract Service",
            "resource": "wathq_service",
            "action": "use",
            "scope": "service",
            "service_slug": "company-contract"
        },
        {
            "name": "use_attorney_services",
            "description": "Use Attorney Services",
            "resource": "wathq_service",
            "action": "use",
            "scope": "service",
            "service_slug": "attorney-services"
        },
        {
            "name": "use_national_address",
            "description": "Use National Address Service",
            "resource": "wathq_service",
            "action": "use",
            "scope": "service",
            "service_slug": "national-address"
        },
        # Tenant management permissions
        {
            "name": "manage_tenant_services",
            "description": "Manage Tenant Services",
            "resource": "tenant_service",
            "action": "manage",
            "scope": "tenant",
            "service_slug": None
        },
        {
            "name": "approve_service_requests",
            "description": "Approve Service Requests",
            "resource": "tenant_service",
            "action": "approve",
            "scope": "tenant",
            "service_slug": None
        },
        {
            "name": "assign_user_services",
            "description": "Assign Services to Users",
            "resource": "user_service",
            "action": "assign",
            "scope": "tenant",
            "service_slug": None
        },
        {
            "name": "view_service_usage",
            "description": "View Service Usage Statistics",
            "resource": "tenant_service",
            "action": "read",
            "scope": "tenant",
            "service_slug": None
        }
    ]
    
    print("Seeding WATHQ permissions...")
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            print(f"Created permission: {perm_data['name']}")
        else:
            print(f"Permission already exists: {perm_data['name']}")
    
    db.commit()


def create_default_roles(db: Session):
    """Create default roles for WATHQ services."""
    
    # Get all permissions
    all_permissions = db.query(Permission).all()
    service_permissions = [p for p in all_permissions if p.resource == "wathq_service"]
    management_permissions = [p for p in all_permissions if p.name in [
        "manage_tenant_services", "approve_service_requests", "assign_user_services"
    ]]
    
    roles_data = [
        {
            "name": "WATHQ Admin",
            "description": "Full access to all WATHQ services and management",
            "permissions": all_permissions,
            "is_default": False
        },
        {
            "name": "WATHQ Manager",
            "description": "Manage tenant services and assign to users",
            "permissions": service_permissions + management_permissions,
            "is_default": False
        },
        {
            "name": "WATHQ User",
            "description": "Basic access to assigned WATHQ services",
            "permissions": service_permissions,
            "is_default": True
        }
    ]
    
    print("Creating default WATHQ roles...")
    for role_data in roles_data:
        # Create system-wide roles (tenant_id = None)
        existing = db.query(Role).filter(
            Role.name == role_data["name"],
            Role.tenant_id.is_(None)
        ).first()
        
        if not existing:
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                tenant_id=None,  # System-wide role
                is_default=role_data["is_default"]
            )
            role.permissions = role_data["permissions"]
            db.add(role)
            print(f"Created role: {role_data['name']}")
        else:
            print(f"Role already exists: {role_data['name']}")
    
    db.commit()


def main():
    """Main function to seed all WATHQ data."""
    db = SessionLocal()
    try:
        print("Starting WATHQ services and permissions seeding...")
        
        seed_wathq_services(db)
        seed_wathq_permissions(db)
        create_default_roles(db)
        
        print("WATHQ seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()