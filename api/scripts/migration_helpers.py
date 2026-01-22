#!/usr/bin/env python3
"""
Helper utilities for database migrations.

Provides common migration tasks and utilities.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationHelpers:
    """Helper class for common migration tasks."""
    
    def __init__(self, alembic_cfg_path: str = "alembic.ini"):
        self.alembic_cfg = Config(alembic_cfg_path)
        self.script = ScriptDirectory.from_config(self.alembic_cfg)
    
    def list_all_revisions(self):
        """List all migration revisions."""
        logger.info("=" * 70)
        logger.info("ALL MIGRATION REVISIONS")
        logger.info("=" * 70)
        
        for revision in self.script.walk_revisions():
            logger.info(f"Revision: {revision.revision}")
            logger.info(f"  Down: {revision.down_revision}")
            logger.info(f"  Message: {revision.doc}")
            logger.info("-" * 70)
    
    def show_history(self, verbose: bool = False):
        """Show migration history."""
        logger.info("Migration History:")
        command.history(self.alembic_cfg, verbose=verbose)
    
    def create_new_migration(self, message: str, autogenerate: bool = True):
        """Create a new migration."""
        logger.info(f"Creating new migration: {message}")
        
        if autogenerate:
            command.revision(
                self.alembic_cfg,
                message=message,
                autogenerate=True
            )
        else:
            command.revision(
                self.alembic_cfg,
                message=message
            )
        
        logger.info("✓ Migration created successfully")
    
    def stamp_database(self, revision: str = "head"):
        """Stamp database with a specific revision without running migrations."""
        logger.info(f"Stamping database with revision: {revision}")
        command.stamp(self.alembic_cfg, revision)
        logger.info("✓ Database stamped successfully")


def main():
    """Main entry point for helper utilities."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migration helper utilities")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List revisions
    subparsers.add_parser("list", help="List all migration revisions")
    
    # Show history
    history_parser = subparsers.add_parser("history", help="Show migration history")
    history_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    # Create migration
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("message", help="Migration message")
    create_parser.add_argument("--no-autogenerate", action="store_true", help="Don't autogenerate")
    
    # Stamp database
    stamp_parser = subparsers.add_parser("stamp", help="Stamp database with revision")
    stamp_parser.add_argument("revision", nargs="?", default="head", help="Revision to stamp")
    
    args = parser.parse_args()
    
    helpers = MigrationHelpers()
    
    if args.command == "list":
        helpers.list_all_revisions()
    elif args.command == "history":
        helpers.show_history(verbose=args.verbose)
    elif args.command == "create":
        helpers.create_new_migration(
            args.message,
            autogenerate=not args.no_autogenerate
        )
    elif args.command == "stamp":
        helpers.stamp_database(args.revision)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
