#!/usr/bin/env python3
"""
Test enhanced authentication system
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.core.security import create_access_token
from app import crud
from jose import jwt
from app.core.config import settings
from app.schemas.user import TokenPayload


def test_enhanced_auth():
    """Test enhanced authentication system."""
    db = SessionLocal()
    try:
        print("Testing enhanced authentication system...")
        
        # Test management user token creation
        mgmt_user = crud.management_user.get_by_email(db, email="superadmin@example.com")
        if mgmt_user:
            mgmt_token = create_access_token(
                subject=mgmt_user.id,
                is_management_user=True,
                is_super_admin=mgmt_user.is_super_admin
            )
            
            # Decode and verify token
            payload = jwt.decode(mgmt_token, settings.SECRET_KEY, algorithms=["HS256"])
            token_data = TokenPayload(**payload)
            
            print(f"Management token created:")
            print(f"  - User ID: {token_data.sub}")
            print(f"  - Is Management User: {token_data.is_management_user}")
            print(f"  - Is Super Admin: {token_data.is_super_admin}")
        
        # Test regular user token creation
        regular_user = crud.user.get_by_email(db, email="admin@example.com", tenant_id=1)
        if regular_user:
            regular_token = create_access_token(
                subject=regular_user.id,
                tenant_id=regular_user.tenant_id,
                tenant_slug="default",
                is_management_user=False,
                is_super_admin=regular_user.is_superuser
            )
            
            # Decode and verify token
            payload = jwt.decode(regular_token, settings.SECRET_KEY, algorithms=["HS256"])
            token_data = TokenPayload(**payload)
            
            print(f"Regular user token created:")
            print(f"  - User ID: {token_data.sub}")
            print(f"  - Tenant ID: {token_data.tenant_id}")
            print(f"  - Is Management User: {token_data.is_management_user}")
            print(f"  - Is Super Admin: {token_data.is_super_admin}")
        
        # Test authentication functions
        print("\nTesting authentication functions...")
        
        # Test management user auth
        mgmt_auth = crud.management_user.authenticate(
            db, email="superadmin@example.com", password="superadmin123"
        )
        print(f"Management user auth: {'SUCCESS' if mgmt_auth else 'FAILED'}")
        
        # Test regular user auth
        regular_auth = crud.user.authenticate(
            db, email="admin@example.com", password="admin123", tenant_id=1
        )
        print(f"Regular user auth: {'SUCCESS' if regular_auth else 'FAILED'}")
        
        print("\nEnhanced authentication system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_enhanced_auth()
    sys.exit(0 if success else 1)