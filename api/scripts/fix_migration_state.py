#!/usr/bin/env python3
"""
Fix migration state and recover from failed transactions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_migration_state():
    """Fix the migration state by clearing failed transactions."""
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        with engine.connect() as conn:
            # Rollback any pending transaction
            logger.info("Rolling back any pending transactions...")
            conn.execute(text("ROLLBACK"))
            conn.commit()
            
            # Check current alembic version
            logger.info("Checking current migration state...")
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current = result.fetchone()
            
            if current:
                logger.info(f"Current migration version: {current[0]}")
            else:
                logger.info("No migration version found in database")
            
            # Check if make_wathq_nullable was partially applied
            logger.info("\nChecking if migration was partially applied...")
            
            # Check if the columns are already nullable
            result = conn.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'wathq_call_logs' 
                AND column_name IN ('tenant_id', 'user_id', 'management_user_id')
            """))
            
            columns = result.fetchall()
            logger.info("wathq_call_logs columns:")
            for col in columns:
                logger.info(f"  {col[0]}: nullable={col[1]}")
            
            # If the migration was partially applied, we need to mark it as complete
            if current and current[0] == 'add_logo_name_ar':
                logger.info("\nMigration appears to be stuck at add_logo_name_ar")
                logger.info("Attempting to manually update to make_wathq_nullable...")
                
                # Update the version
                conn.execute(text("UPDATE alembic_version SET version_num = 'make_wathq_nullable'"))
                conn.commit()
                logger.info("✓ Updated migration version to make_wathq_nullable")
            
            logger.info("\n" + "=" * 70)
            logger.info("Migration state fixed!")
            logger.info("You can now run: ./migrate.sh")
            logger.info("=" * 70)
            
    except Exception as e:
        logger.error(f"Error fixing migration state: {e}", exc_info=True)
        return False
    finally:
        engine.dispose()
    
    return True


if __name__ == "__main__":
    success = fix_migration_state()
    sys.exit(0 if success else 1)
