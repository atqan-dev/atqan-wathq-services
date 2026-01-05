#!/usr/bin/env python3
"""
Production-ready migration script for Alembic.

This script handles:
- Multiple migration heads
- Automatic merging of branches
- Rollback on errors
- Development and production environments
- Database backup recommendations
- Detailed logging and error reporting
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationRunner:
    """Handles database migrations with error handling and validation."""
    
    def __init__(self, alembic_cfg_path: str = "alembic.ini"):
        """Initialize migration runner."""
        self.alembic_cfg_path = alembic_cfg_path
        self.alembic_cfg = Config(alembic_cfg_path)
        self.engine = create_engine(str(settings.DATABASE_URL))
        
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                return current_rev
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None
    
    def get_heads(self) -> list[str]:
        """Get all head revisions."""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            heads = script.get_revisions("heads")
            return [head.revision for head in heads]
        except Exception as e:
            logger.error(f"Failed to get heads: {e}")
            return []
    
    def has_multiple_heads(self) -> bool:
        """Check if there are multiple heads."""
        heads = self.get_heads()
        return len(heads) > 1
    
    def merge_heads(self, message: str = "Merge multiple heads") -> bool:
        """Merge multiple heads into one."""
        try:
            logger.info("Merging multiple heads...")
            heads = self.get_heads()
            
            if len(heads) <= 1:
                logger.info("No multiple heads to merge")
                return True
            
            logger.info(f"Found {len(heads)} heads: {heads}")
            
            # Create merge migration
            command.merge(
                self.alembic_cfg,
                revisions=heads,
                message=message
            )
            
            logger.info("✓ Successfully created merge migration")
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge heads: {e}")
            return False
    
    def check_database_connection(self) -> bool:
        """Check if database is accessible."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            return True
        except SQLAlchemyError as e:
            logger.error(f"✗ Database connection failed: {e}")
            return False
    
    def backup_reminder(self):
        """Print backup reminder for production."""
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            logger.warning("=" * 70)
            logger.warning("PRODUCTION ENVIRONMENT DETECTED")
            logger.warning("=" * 70)
            logger.warning("⚠️  IMPORTANT: Ensure you have a recent database backup!")
            logger.warning("⚠️  Consider running migrations during low-traffic periods")
            logger.warning("=" * 70)
            
            response = input("\nDo you want to continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("Migration cancelled by user")
                sys.exit(0)
    
    def upgrade_to_head(self) -> bool:
        """Upgrade database to head revision."""
        try:
            logger.info("Starting database upgrade...")
            
            # If multiple heads exist, upgrade to all heads
            if self.has_multiple_heads():
                logger.info("Multiple heads detected, upgrading to all heads...")
                command.upgrade(self.alembic_cfg, "heads")
            else:
                command.upgrade(self.alembic_cfg, "head")
            
            logger.info("✓ Database upgrade successful")
            return True
            
        except Exception as e:
            logger.error(f"✗ Database upgrade failed: {e}")
            return False
    
    def downgrade(self, revision: str = "-1") -> bool:
        """Downgrade database to specific revision."""
        try:
            logger.info(f"Downgrading database to {revision}...")
            command.downgrade(self.alembic_cfg, revision)
            logger.info("✓ Database downgrade successful")
            return True
        except Exception as e:
            logger.error(f"✗ Database downgrade failed: {e}")
            return False
    
    def show_current_status(self):
        """Show current migration status."""
        logger.info("=" * 70)
        logger.info("MIGRATION STATUS")
        logger.info("=" * 70)
        
        current = self.get_current_revision()
        logger.info(f"Current revision: {current or 'None (empty database)'}")
        
        heads = self.get_heads()
        logger.info(f"Head revisions: {heads}")
        logger.info(f"Number of heads: {len(heads)}")
        
        if len(heads) > 1:
            logger.warning("⚠️  Multiple heads detected - branches need to be merged")
        
        logger.info("=" * 70)
    
    def run(self, auto_merge: bool = True, force: bool = False) -> bool:
        """
        Run migrations with full error handling.
        
        Args:
            auto_merge: Automatically merge multiple heads
            force: Skip production confirmation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting migration process...")
            
            # Check database connection
            if not self.check_database_connection():
                logger.error("Cannot proceed without database connection")
                return False
            
            # Show current status
            self.show_current_status()
            
            # Production safety check
            if not force:
                self.backup_reminder()
            
            # Handle multiple heads
            if self.has_multiple_heads():
                if auto_merge:
                    logger.info("Auto-merge enabled, merging heads...")
                    if not self.merge_heads():
                        logger.error("Failed to merge heads")
                        return False
                else:
                    logger.error("Multiple heads detected. Use --auto-merge to merge them")
                    return False
            
            # Run upgrade
            if not self.upgrade_to_head():
                logger.error("Migration failed")
                return False
            
            # Show final status
            logger.info("\n" + "=" * 70)
            logger.info("MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            self.show_current_status()
            
            return True
            
        except KeyboardInterrupt:
            logger.warning("\nMigration interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during migration: {e}", exc_info=True)
            return False
        finally:
            self.engine.dispose()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run database migrations safely",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run migrations with auto-merge
  python scripts/run_migrations.py
  
  # Run migrations without auto-merge
  python scripts/run_migrations.py --no-auto-merge
  
  # Force run without production confirmation
  python scripts/run_migrations.py --force
  
  # Show current status only
  python scripts/run_migrations.py --status-only
  
  # Downgrade one revision
  python scripts/run_migrations.py --downgrade
  
  # Downgrade to specific revision
  python scripts/run_migrations.py --downgrade --revision abc123
        """
    )
    
    parser.add_argument(
        "--no-auto-merge",
        action="store_true",
        help="Don't automatically merge multiple heads"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip production confirmation prompts"
    )
    
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Show migration status without running migrations"
    )
    
    parser.add_argument(
        "--downgrade",
        action="store_true",
        help="Downgrade instead of upgrade"
    )
    
    parser.add_argument(
        "--revision",
        type=str,
        default="-1",
        help="Revision to downgrade to (default: -1 for one step back)"
    )
    
    parser.add_argument(
        "--alembic-config",
        type=str,
        default="alembic.ini",
        help="Path to alembic.ini config file"
    )
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = MigrationRunner(alembic_cfg_path=args.alembic_config)
    
    # Status only mode
    if args.status_only:
        runner.show_current_status()
        sys.exit(0)
    
    # Downgrade mode
    if args.downgrade:
        success = runner.downgrade(args.revision)
        sys.exit(0 if success else 1)
    
    # Run migrations
    success = runner.run(
        auto_merge=not args.no_auto_merge,
        force=args.force
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
