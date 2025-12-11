#!/usr/bin/env python3
"""
Test single schema multitenancy
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.core.multitenancy import set_current_tenant, get_current_tenant


def test_single_schema():
    """Test single schema multitenancy functionality."""
    db = SessionLocal()
    try:
        print("Testing single schema multitenancy...")
        
        # List all tenants
        tenants = db.query(Tenant).all()
        print(f"Found {len(tenants)} tenants:")
        for tenant in tenants:
            print(f"  - {tenant.name} (slug: {tenant.slug}, id: {tenant.id})")
        
        # Test tenant context
        if tenants:
            test_tenant = tenants[0]
            set_current_tenant(test_tenant.id, test_tenant.slug)
            current = get_current_tenant()
            print(f"Set current tenant: {current.tenant_slug} (ID: {current.tenant_id})")
        
        # List users by tenant
        for tenant in tenants:
            users = db.query(User).filter(User.tenant_id == tenant.id).all()
            print(f"Tenant '{tenant.name}' has {len(users)} users:")
            for user in users:
                print(f"  - {user.email} (ID: {user.id})")
        
        print("Single schema multitenancy test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = test_single_schema()
    sys.exit(0 if success else 1)