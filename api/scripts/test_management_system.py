#!/usr/bin/env python3
"""
Test management users system
"""
import sys
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent.parent  # Go up one level from scripts/ to backend/
sys.path.insert(0, str(current_dir))

# Also add the current directory as fallback
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.management_user import ManagementUser
from app.models.tenant import Tenant
from app.models.user import User
from app import crud


def test_management_system():
    """Test management users system functionality."""
    db = SessionLocal()
    try:
        print("Testing management users system...")

        # Test management users
        management_users = db.query(ManagementUser).all()
        print(f"Found {len(management_users)} management users:")
        for user in management_users:
            print(f"  - {user.email} (Super Admin: {user.is_super_admin}, Active: {user.is_active})")

        # Test authentication
        if management_users:
            test_user = management_users[0]
            auth_result = crud.management_user.authenticate(
                db, email=test_user.email, password="superadmin123"
            )
            print(f"Authentication test: {'SUCCESS' if auth_result else 'FAILED'}")

        # Test tenant management capabilities
        tenants = db.query(Tenant).all()
        print(f"Management can see {len(tenants)} tenants:")
        for tenant in tenants:
            users_count = db.query(User).filter(User.tenant_id == tenant.id).count()
            print(f"  - {tenant.name} ({tenant.slug}): {users_count} users")

        # Test cross-tenant user management
        all_users = db.query(User).all()
        print(f"Management can see {len(all_users)} total users across all tenants")

        print("Management system test completed successfully!")
        return True

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_management_system()
    sys.exit(0 if success else 1)
