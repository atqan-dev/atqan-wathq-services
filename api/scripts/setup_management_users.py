#!/usr/bin/env python3
"""
Setup management users table and create default super admin
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
from app.core.security import get_password_hash
from app.db.base import Base
from sqlalchemy import create_engine
from app.core.config import settings


def setup_management_users():
    """Setup management users table and create default super admin."""
    try:
        print("Setting up management users...")
        
        # Create tables
        database_url = str(settings.DATABASE_URL)
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(database_url)
        Base.metadata.create_all(bind=engine)
        print("Created management_users table")
        
        # Create default super admin
        db = SessionLocal()
        try:
            existing_admin = db.query(ManagementUser).filter(
                ManagementUser.email == "superadmin@example.com"
            ).first()
            
            if not existing_admin:
                super_admin = ManagementUser(
                    email="superadmin@example.com",
                    first_name="Super",
                    last_name="Admin",
                    hashed_password=get_password_hash("superadmin123"),
                    is_active=True,
                    is_super_admin=True
                )
                db.add(super_admin)
                db.commit()
                db.refresh(super_admin)
                print(f"Created super admin: {super_admin.email} with password 'superadmin123'")
            else:
                print(f"Super admin already exists: {existing_admin.email}")
                
        finally:
            db.close()
        
        print("Management users setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = setup_management_users()
    sys.exit(0 if success else 1)