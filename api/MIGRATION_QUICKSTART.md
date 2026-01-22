# Migration Quick Start Guide

## 🚀 Run Migrations Now

```bash
# Simple one-command migration (recommended)
./migrate.sh

# Or using Python directly
uv run python scripts/run_migrations.py

# Or using the traditional way (if no multiple heads)
uv run alembic upgrade head
```

## 📋 Common Commands

### Check Status
```bash
# Show current migration status
uv run python scripts/run_migrations.py --status-only

# Show migration history
uv run python scripts/migration_helpers.py history
```

### Run Migrations
```bash
# Development (with auto-merge)
./migrate.sh

# Production (with confirmation)
ENVIRONMENT=production ./migrate.sh

# CI/CD (skip confirmation)
./migrate.sh --force
```

### Create New Migration
```bash
# Auto-generate from model changes
uv run python scripts/migration_helpers.py create "add new feature"

# Or use alembic directly
uv run alembic revision --autogenerate -m "add new feature"
```

### Rollback
```bash
# Rollback one step
uv run python scripts/run_migrations.py --downgrade

# Rollback to specific revision
uv run python scripts/run_migrations.py --downgrade --revision abc123
```

## 🛠️ Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `migrate.sh` | Simple wrapper for migrations | `./migrate.sh` |
| `scripts/run_migrations.py` | Full-featured migration runner | `uv run python scripts/run_migrations.py` |
| `scripts/migration_helpers.py` | Helper utilities | `uv run python scripts/migration_helpers.py list` |

## 🔧 Troubleshooting

### Multiple Heads Error
```bash
# The script handles this automatically
./migrate.sh
```

### Database Connection Error
```bash
# Check your .env file has correct DATABASE_URL
cat .env | grep DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Migration Failed
```bash
# Check status
uv run python scripts/run_migrations.py --status-only

# Rollback if needed
uv run python scripts/run_migrations.py --downgrade

# Fix and retry
./migrate.sh
```

## 📚 Full Documentation

See `scripts/README_MIGRATIONS.md` for complete documentation.

## ⚡ Quick Examples

```bash
# First time setup
./migrate.sh

# Before deploying
./migrate.sh --status-only  # Check what will run
./migrate.sh                # Apply migrations

# After adding new models
uv run python scripts/migration_helpers.py create "add user preferences"
./migrate.sh

# Emergency rollback
uv run python scripts/run_migrations.py --downgrade
```

## 🎯 Production Checklist

- [ ] Backup database
- [ ] Test in staging
- [ ] Review migration files
- [ ] Run during low-traffic period
- [ ] Monitor application after migration
- [ ] Have rollback plan ready

```bash
# Production deployment
pg_dump -U postgres -d dbname > backup_$(date +%Y%m%d_%H%M%S).sql
ENVIRONMENT=production ./migrate.sh
```
