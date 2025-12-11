#!/usr/bin/env python3
"""
Verify fresh migration results
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.management_user import ManagementUser
from app.models.permission import Permission, Role
from app import crud


def verify_migration():
    """Verify fresh migration results."""
    db = SessionLocal()
    try:
        print("Verifying fresh migration...")
        
        # Check tenants
        tenants = db.query(Tenant).all()
        print(f"Tenants: {len(tenants)}")
        for tenant in tenants:
            print(f"  - {tenant.name} ({tenant.slug}) - Active: {tenant.is_active}")
        
        # Check regular users
        users = db.query(User).all()
        print(f"Regular users: {len(users)}")
        for user in users:
            print(f"  - {user.email} (Tenant: {user.tenant_id}, Super: {user.is_superuser})")
        
        # Check management users
        mgmt_users = db.query(ManagementUser).all()
        print(f"Management users: {len(mgmt_users)}")
        for user in mgmt_users:
            print(f"  - {user.email} (Super Admin: {user.is_super_admin})")
        
        # Check permissions
        permissions = db.query(Permission).all()
        print(f"Permissions: {len(permissions)}")
        for perm in permissions:
            print(f"  - {perm.name}: {perm.resource}.{perm.action}")
        
        # Check roles
        roles = db.query(Role).all()
        print(f"Roles: {len(roles)}")
        for role in roles:
            print(f"  - {role.name} (Tenant: {role.tenant_id}, Default: {role.is_default})")
        
        # Test authentication
        print("\n--- Authentication Tests ---")
        
        # Test regular user auth
        regular_auth = crud.user.authenticate(
            db, email="admin@example.com", password="admin123", tenant_id=1
        )
        print(f"Regular user auth: {'SUCCESS' if regular_auth else 'FAILED'}")
        
        # Test management user auth
        mgmt_auth = crud.management_user.authenticate(
            db, email="superadmin@example.com", password="superadmin123"
        )
        print(f"Management user auth: {'SUCCESS' if mgmt_auth else 'FAILED'}")
        
        print("\n--- Database Schema Verification ---")
        
        # Check table existence
        from sqlalchemy import text
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        result = db.execute(tables_query)
        tables = [row[0] for row in result.fetchall()]
        print(f"Database tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
        
        expected_tables = [
            'tenants', 'users', 'management_users', 
            'permissions', 'roles', 'role_permissions', 'user_roles'
        ]
        
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
            return False
        
        print("\nFresh migration verification completed successfully!")
        print("\nSystem is ready with:")
        print("- Single schema multitenancy")
        print("- Management users system")
        print("- Default tenant and users")
        print("- Permissions and roles")
        
        return True
        
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = verify_migration()
    sys.exit(0 if success else 1)