#!/usr/bin/env python3
"""
Fresh database migration - clear all and recreate
"""

import sys
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent.parent  # Go up one level from scripts/ to backend/
sys.path.insert(0, str(current_dir))

# Also add the current directory as fallback
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models import *  # Import all models
from app.core.security import get_password_hash


def fresh_migration():
    """Clear database and recreate all tables with fresh data."""
    try:
        print("Starting fresh database migration...")
        
        # Create engine
        database_url = str(settings.DATABASE_URL)
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(database_url)
        
        # Drop all tables
        print("Dropping all existing tables...")
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            conn.commit()
        
        # Create all tables
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create initial data
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        try:
            # Create default tenant
            from app.models.tenant import Tenant
            default_tenant = Tenant(
                name="Default",
                slug="default",
                description="Default tenant for the application",
                is_active=True,
                max_users=1000
            )
            db.add(default_tenant)
            db.commit()
            db.refresh(default_tenant)
            print(f"Created default tenant (ID: {default_tenant.id})")
            
            # Create super admin user
            from app.models.user import User
            super_user = User(
                email="admin@example.com",
                first_name="Super",
                last_name="User",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
                tenant_id=default_tenant.id
            )
            db.add(super_user)
            db.commit()
            db.refresh(super_user)
            print(f"Created super user: {super_user.email}")
            
            # Create management super admin
            from app.models.management_user import ManagementUser
            management_admin = ManagementUser(
                email="superadmin@example.com",
                first_name="Super",
                last_name="Admin",
                hashed_password=get_password_hash("superadmin123"),
                is_active=True,
                is_super_admin=True
            )
            db.add(management_admin)
            db.commit()
            db.refresh(management_admin)
            print(f"Created management super admin: {management_admin.email}")
            
            # Create default permissions
            from app.models.permission import Permission
            default_permissions = [
                {"name": "read_users", "description": "Read users", "resource": "user", "action": "read"},
                {"name": "create_users", "description": "Create users", "resource": "user", "action": "create"},
                {"name": "update_users", "description": "Update users", "resource": "user", "action": "update"},
                {"name": "delete_users", "description": "Delete users", "resource": "user", "action": "delete"},
                {"name": "manage_tenant", "description": "Manage tenant", "resource": "tenant", "action": "manage"},
            ]
            
            for perm_data in default_permissions:
                permission = Permission(**perm_data)
                db.add(permission)
            
            db.commit()
            print(f"Created {len(default_permissions)} default permissions")
            
            # Create default roles
            from app.models.permission import Role
            admin_role = Role(
                name="admin",
                description="Administrator role",
                tenant_id=default_tenant.id,
                is_default=False,
                is_active=True
            )
            db.add(admin_role)
            
            user_role = Role(
                name="user",
                description="Regular user role",
                tenant_id=default_tenant.id,
                is_default=True,
                is_active=True
            )
            db.add(user_role)
            
            db.commit()
            print("Created default roles")
            
        finally:
            db.close()
        
        print("Fresh migration completed successfully!")
        print("\nDefault credentials:")
        print("- Regular user: admin@example.com / admin123")
        print("- Management user: superadmin@example.com / superadmin123")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = fresh_migration()
    sys.exit(0 if success else 1)