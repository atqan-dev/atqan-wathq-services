#!/usr/bin/env python3
"""
Stamp database to skip problematic migration and continue with remaining migrations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from alembic import command
from alembic.config import Config
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def stamp_and_migrate():
    """Stamp the database to skip problematic migration and continue."""
    engine = create_engine(str(settings.DATABASE_URL))
    alembic_cfg = Config("alembic.ini")
    
    try:
        with engine.connect() as conn:
            # First, rollback any pending transaction
            logger.info("Rolling back any pending transactions...")
            try:
                conn.execute(text("ROLLBACK"))
                conn.commit()
            except:
                pass
            
            # Check current version
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current = result.fetchone()
            logger.info(f"Current version: {current[0] if current else 'None'}")
            
            # Check if make_wathq_nullable changes are already applied
            result = conn.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'wathq_call_logs' 
                AND column_name IN ('tenant_id', 'user_id')
            """))
            columns = {row[0]: row[1] for row in result.fetchall()}
            
            if columns.get('tenant_id') == 'YES' and columns.get('user_id') == 'YES':
                logger.info("✓ make_wathq_nullable changes are already applied")
                logger.info("Stamping database to mark migration as complete...")
                
                # Update to make_wathq_nullable
                conn.execute(text("UPDATE alembic_version SET version_num = 'make_wathq_nullable'"))
                conn.commit()
                logger.info("✓ Stamped to make_wathq_nullable")
            
        # Now run remaining migrations using alembic
        logger.info("\nRunning remaining migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("✓ All migrations completed successfully!")
        
        # Show final status
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            final = result.fetchone()
            logger.info(f"\nFinal version: {final[0] if final else 'None'}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("FIXING MIGRATION STATE AND RUNNING MIGRATIONS")
    logger.info("=" * 70)
    success = stamp_and_migrate()
    logger.info("=" * 70)
    if success:
        logger.info("✓ SUCCESS! All migrations completed")
    else:
        logger.info("✗ FAILED - Check errors above")
    logger.info("=" * 70)
    sys.exit(0 if success else 1)
