#!/usr/bin/env python3
"""
Migration script to convert from schema-based to single schema multitenancy
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.models.tenant import Tenant
from sqlalchemy import text


def migrate_to_single_schema():
    """Migrate from schema-based to single schema multitenancy."""
    db = SessionLocal()
    try:
        print("Starting migration to single schema multitenancy...")
        
        # Check if schema_name column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tenants' AND column_name = 'schema_name'
        """))
        
        if result.fetchone():
            print("Removing schema_name column from tenants table...")
            db.execute(text("ALTER TABLE tenants DROP COLUMN IF EXISTS schema_name"))
            db.commit()
            print("Removed schema_name column")
        
        # Ensure default tenant exists
        default_tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
        if not default_tenant:
            print("Creating default tenant...")
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
            print(f"Created default tenant with ID: {default_tenant.id}")
        else:
            print(f"Default tenant already exists with ID: {default_tenant.id}")
        
        # Update any users without tenant_id to use default tenant
        result = db.execute(text("""
            UPDATE users 
            SET tenant_id = :tenant_id 
            WHERE tenant_id IS NULL
        """), {"tenant_id": default_tenant.id})
        
        updated_users = result.rowcount
        if updated_users > 0:
            print(f"Updated {updated_users} users to use default tenant")
        
        db.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = migrate_to_single_schema()
    sys.exit(0 if success else 1)