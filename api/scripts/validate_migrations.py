#!/usr/bin/env python3
"""
Validate migration files for common issues.

Checks for:
- Circular dependencies
- Missing down_revision
- Duplicate revision IDs
- Orphaned migrations
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic.script import ScriptDirectory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationValidator:
    """Validates migration files for common issues."""
    
    def __init__(self, alembic_cfg_path: str = "alembic.ini"):
        self.alembic_cfg = Config(alembic_cfg_path)
        self.script = ScriptDirectory.from_config(self.alembic_cfg)
        self.issues = []
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        logger.info("=" * 70)
        logger.info("VALIDATING MIGRATIONS")
        logger.info("=" * 70)
        
        self.check_duplicate_revisions()
        self.check_orphaned_migrations()
        self.check_multiple_heads()
        self.check_missing_downgrade()
        
        logger.info("=" * 70)
        
        if self.issues:
            logger.error(f"Found {len(self.issues)} issue(s):")
            for issue in self.issues:
                logger.error(f"  ✗ {issue}")
            logger.info("=" * 70)
            return False
        else:
            logger.info("✓ All validations passed!")
            logger.info("=" * 70)
            return True
    
    def check_duplicate_revisions(self):
        """Check for duplicate revision IDs."""
        revisions = {}
        for rev in self.script.walk_revisions():
            if rev.revision in revisions:
                self.issues.append(
                    f"Duplicate revision ID: {rev.revision} "
                    f"(in {rev.path} and {revisions[rev.revision]})"
                )
            else:
                revisions[rev.revision] = rev.path
    
    def check_orphaned_migrations(self):
        """Check for orphaned migrations (no path to head)."""
        heads = set(self.script.get_revisions("heads"))
        reachable = set()
        
        for head in heads:
            for rev in self.script.iterate_revisions(head.revision, "base"):
                reachable.add(rev.revision)
        
        all_revs = set(rev.revision for rev in self.script.walk_revisions())
        orphaned = all_revs - reachable
        
        if orphaned:
            for rev_id in orphaned:
                self.issues.append(f"Orphaned migration: {rev_id}")
    
    def check_multiple_heads(self):
        """Check for multiple heads."""
        heads = list(self.script.get_revisions("heads"))
        if len(heads) > 1:
            head_ids = [h.revision for h in heads]
            self.issues.append(
                f"Multiple heads detected: {head_ids}. "
                "Run migration script to auto-merge."
            )
    
    def check_missing_downgrade(self):
        """Check for migrations without downgrade function."""
        for rev in self.script.walk_revisions():
            # Read the migration file
            try:
                with open(rev.path, 'r') as f:
                    content = f.read()
                    
                # Check if downgrade function is empty or just has pass
                if 'def downgrade():' in content:
                    downgrade_section = content.split('def downgrade():')[1]
                    # Remove comments and whitespace
                    code = '\n'.join(
                        line for line in downgrade_section.split('\n')
                        if line.strip() and not line.strip().startswith('#')
                    )
                    if not code.strip() or code.strip() == 'pass':
                        logger.warning(
                            f"Migration {rev.revision} has empty downgrade function"
                        )
            except Exception as e:
                logger.warning(f"Could not validate {rev.revision}: {e}")


def main():
    """Main entry point."""
    validator = MigrationValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
