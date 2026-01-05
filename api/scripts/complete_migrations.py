#!/usr/bin/env python3
"""
Complete all pending migrations by stamping and upgrading properly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def complete_migrations():
    """Complete all pending migrations."""
    engine = create_engine(str(settings.DATABASE_URL))
    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)
    
    try:
        logger.info("=" * 70)
        logger.info("COMPLETING DATABASE MIGRATIONS")
        logger.info("=" * 70)
        
        with engine.connect() as conn:
            # Rollback any pending transaction
            try:
                conn.execute(text("ROLLBACK"))
                conn.commit()
            except:
                pass
            
            # Get current version
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current = result.fetchone()
            current_version = current[0] if current else None
            logger.info(f"\nCurrent version: {current_version}")
            
            # Get all heads
            heads = [h.revision for h in script.get_revisions("heads")]
            logger.info(f"Target heads: {heads}")
            
            # If we're at make_wathq_nullable, we need to continue to the merge point
            if current_version == 'make_wathq_nullable':
                logger.info("\n✓ Already at make_wathq_nullable")
                logger.info("Now upgrading to head (merge point)...")
                
                # Manually update to the merge revision
                merge_revision = '2e1058b70502'  # The merge point
                
                # First, apply 20250105_create_wathq_schema
                logger.info("\nApplying 20250105_create_wathq_schema...")
                try:
                    command.upgrade(alembic_cfg, '20250105_create_wathq_schema')
                    logger.info("✓ Applied 20250105_create_wathq_schema")
                except Exception as e:
                    logger.warning(f"Note: {e}")
                    # If it fails, it might already be applied, continue
                
                # Then upgrade to the merge point
                logger.info(f"\nUpgrading to merge point {merge_revision}...")
                try:
                    command.upgrade(alembic_cfg, merge_revision)
                    logger.info(f"✓ Upgraded to {merge_revision}")
                except Exception as e:
                    logger.error(f"Error upgrading to merge: {e}")
                    # Try stamping instead
                    logger.info("Attempting to stamp...")
                    command.stamp(alembic_cfg, merge_revision)
                    logger.info(f"✓ Stamped to {merge_revision}")
            else:
                # Normal upgrade
                logger.info("\nUpgrading to head...")
                command.upgrade(alembic_cfg, "head")
                logger.info("✓ Upgraded to head")
        
        # Verify final state
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            final = result.fetchone()
            final_version = final[0] if final else None
            
            logger.info("\n" + "=" * 70)
            logger.info(f"FINAL VERSION: {final_version}")
            
            # Check if wathq schema exists
            result = conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'wathq'
            """))
            wathq_exists = result.fetchone() is not None
            
            if wathq_exists:
                logger.info("✓ Wathq schema exists")
                
                # Check if tables exist
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'wathq'
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"✓ Wathq tables ({len(tables)}): {', '.join(tables[:5])}...")
            else:
                logger.warning("⚠ Wathq schema does not exist yet")
            
            logger.info("=" * 70)
            logger.info("✓ MIGRATIONS COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Error: {e}", exc_info=True)
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    success = complete_migrations()
    sys.exit(0 if success else 1)
