"""
Fix the alembic version for cr_requests migration.
This script updates the alembic_version table to remove the old cs_requests revision.
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_cr_requests_migration():
    """Fix the migration state by updating alembic_version."""
    database_url = str(settings.DATABASE_URL)
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check current version
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.fetchone()
            print(f"Current version: {current_version}")
            
            # Check if the old cs_requests revision exists
            if current_version and '20250111_cs_requests' in str(current_version[0]):
                print("Found old cs_requests revision, updating to cr_requests...")
                # Update to the previous revision (before cs_requests)
                conn.execute(text("UPDATE alembic_version SET version_num = '20250108_employees'"))
                conn.commit()
                print("Updated alembic_version to 20250108_employees")
                print("Now you can run: uv run alembic upgrade head")
            else:
                print("No cs_requests revision found in alembic_version")
                print(f"Current version is: {current_version}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    fix_cr_requests_migration()
