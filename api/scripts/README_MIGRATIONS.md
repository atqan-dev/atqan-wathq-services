# Database Migration Guide

This guide explains how to safely run database migrations in development and production environments.

## Quick Start

### Run Migrations (Recommended)

```bash
# Using the migration script (handles multiple heads automatically)
uv run python scripts/run_migrations.py

# Or using uv directly
cd /path/to/api
uv run python scripts/run_migrations.py
```

### Check Migration Status

```bash
# Show current migration status
uv run python scripts/run_migrations.py --status-only

# Show migration history
uv run python scripts/migration_helpers.py history
```

## Migration Scripts

### 1. `run_migrations.py` - Main Migration Script

Production-ready script that handles all migration scenarios.

**Features:**
- ✅ Automatic multiple head detection and merging
- ✅ Database connection validation
- ✅ Production safety checks with confirmation prompts
- ✅ Detailed logging and error reporting
- ✅ Rollback capabilities
- ✅ Environment-aware (dev/prod)

**Usage:**

```bash
# Run migrations with auto-merge (recommended)
uv run python scripts/run_migrations.py

# Run without auto-merge (manual control)
uv run python scripts/run_migrations.py --no-auto-merge

# Force run without confirmation (CI/CD)
uv run python scripts/run_migrations.py --force

# Show status only
uv run python scripts/run_migrations.py --status-only

# Downgrade one step
uv run python scripts/run_migrations.py --downgrade

# Downgrade to specific revision
uv run python scripts/run_migrations.py --downgrade --revision abc123
```

### 2. `migration_helpers.py` - Helper Utilities

Provides common migration management tasks.

**Usage:**

```bash
# List all migration revisions
uv run python scripts/migration_helpers.py list

# Show migration history
uv run python scripts/migration_helpers.py history

# Show verbose history
uv run python scripts/migration_helpers.py history -v

# Create new migration
uv run python scripts/migration_helpers.py create "add new table"

# Create empty migration (no autogenerate)
uv run python scripts/migration_helpers.py create "custom migration" --no-autogenerate

# Stamp database with revision
uv run python scripts/migration_helpers.py stamp head
```

## Common Scenarios

### First Time Setup

```bash
# 1. Check database connection
uv run python scripts/run_migrations.py --status-only

# 2. Run migrations
uv run python scripts/run_migrations.py
```

### Multiple Heads Issue

If you see "Multiple head revisions are present":

```bash
# The script handles this automatically
uv run python scripts/run_migrations.py

# Or manually merge
uv run alembic merge heads -m "merge heads"
uv run alembic upgrade head
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
uv run python scripts/migration_helpers.py create "add user profile table"

# Or use alembic directly
uv run alembic revision --autogenerate -m "add user profile table"
```

### Rollback Migrations

```bash
# Rollback one step
uv run python scripts/run_migrations.py --downgrade

# Rollback to specific revision
uv run python scripts/run_migrations.py --downgrade --revision abc123

# Or use alembic directly
uv run alembic downgrade -1
uv run alembic downgrade abc123
```

### Production Deployment

```bash
# 1. Backup database first!
pg_dump -U postgres -d your_database > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Set environment
export ENVIRONMENT=production

# 3. Run migrations (will prompt for confirmation)
uv run python scripts/run_migrations.py

# 4. Or skip confirmation in CI/CD
uv run python scripts/run_migrations.py --force
```

## Environment Variables

Set these in your `.env` file:

```bash
# Database connection
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname

# Environment (affects safety prompts)
ENVIRONMENT=development  # or production
```

## Troubleshooting

### Issue: "Multiple head revisions are present"

**Solution:**
```bash
uv run python scripts/run_migrations.py
# The script will automatically merge heads
```

### Issue: "Database connection failed"

**Solution:**
1. Check DATABASE_URL in .env
2. Ensure PostgreSQL is running
3. Verify credentials and database exists

```bash
# Test connection
psql -U postgres -d your_database -c "SELECT 1"
```

### Issue: Migration fails midway

**Solution:**
```bash
# Check current state
uv run python scripts/run_migrations.py --status-only

# Rollback if needed
uv run python scripts/run_migrations.py --downgrade

# Fix the migration file and try again
uv run python scripts/run_migrations.py
```

### Issue: Need to skip a migration

**Solution:**
```bash
# Stamp database to mark migration as applied without running it
uv run python scripts/migration_helpers.py stamp <revision_id>
```

## Best Practices

### Development

1. **Always review auto-generated migrations** before applying
2. **Test migrations on a copy of production data** when possible
3. **Keep migrations small and focused** on one change
4. **Add data migrations separately** from schema migrations
5. **Never edit applied migrations** - create new ones instead

### Production

1. **Always backup database** before migrations
2. **Test migrations in staging** environment first
3. **Run during low-traffic periods** when possible
4. **Monitor application** after migration
5. **Have rollback plan ready**
6. **Use the migration script** for safety features

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run Database Migrations
  run: |
    export ENVIRONMENT=production
    uv run python scripts/run_migrations.py --force
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Migration File Structure

```python
"""Brief description

Revision ID: abc123
Revises: xyz789
Create Date: 2025-01-05 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'xyz789'  # Previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Schema changes here
    pass

def downgrade():
    # Reverse changes here
    pass
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- Project-specific migration patterns in `alembic/versions/`

## Support

For issues or questions:
1. Check this documentation
2. Review existing migrations for patterns
3. Check application logs
4. Contact the development team
