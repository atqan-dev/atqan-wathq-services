# Commercial Registration Historical Data Changes

## Overview
Modified the WATHQ commercial registration sync functionality to maintain historical records for each CR number instead of updating existing records. This allows tracking changes over time.

## Changes Made

### 1. Database Schema Changes

#### `commercial_registrations` table:
- **Removed** `unique` constraint from `cr_number` column
- **Added** `fetched_at` timestamp column to track when data was fetched from Wathq
- **Added** composite index on `(cr_number, fetched_at)` for efficient queries

**Migration file**: `api/alembic/versions/20250121_remove_unique_constraint_cr_number.py`

To apply the migration:
```bash
cd api
alembic upgrade head
```

### 2. Model Changes

**File**: `api/app/models/wathq_commercial_registration.py`

- Line 20: Removed `unique=True` from `cr_number` column
- Line 23: Added `fetched_at` column

### 3. Sync Logic Changes

**File**: `api/app/api/v1/endpoints/wathq_sync.py`

- **Removed** `_update_commercial_registration()` function - no longer needed
- **Modified** sync logic to always create new records instead of updating
- **Added** duplicate check based on `(cr_number, fetched_at)` to prevent syncing the same log twice
- **Added** `fetched_at` timestamp to each CR record from the call log

## Benefits

1. **Historical Tracking**: Keep all versions of CR data over time
2. **Audit Trail**: See how CR data changed with timestamps
3. **Data Analysis**: Compare old vs new data for the same CR number
4. **No Data Loss**: Never overwrite existing records

## Data Structure

### Before:
```
CR Number | Name | Status | ...
1010711252 | Company A | Active | ...
```
(Only one record per CR number - updates overwrite)

### After:
```
CR Number | Name | Status | Fetched At | ...
1010711252 | Company A | Active | 2026-01-15 10:00 | ...
1010711252 | Company A | Suspended | 2026-01-20 14:30 | ...
1010711252 | Company B | Active | 2026-01-21 09:15 | ...
```
(Multiple records per CR number - each with its own timestamp)

## Querying Historical Data

### Get latest record for a CR number:
```sql
SELECT * FROM wathq.commercial_registrations
WHERE cr_number = '1010711252'
ORDER BY fetched_at DESC
LIMIT 1;
```

### Get all historical records for a CR number:
```sql
SELECT * FROM wathq.commercial_registrations
WHERE cr_number = '1010711252'
ORDER BY fetched_at DESC;
```

### Compare changes between two dates:
```sql
SELECT * FROM wathq.commercial_registrations
WHERE cr_number = '1010711252'
  AND fetched_at BETWEEN '2026-01-01' AND '2026-01-31'
ORDER BY fetched_at;
```

## Related Tables

All related tables (parties, activities, capital_info, etc.) use `cr_id` as foreign key, which correctly references the `id` column of `commercial_registrations`. Each historical CR record will have its own set of related records.

## Important Notes

- The sync process will skip records that have already been synced (same `cr_number` and `fetched_at`)
- Each call log creates a new CR record with all related data
- Foreign key relationships remain intact - all related tables reference `cr_id` (not `cr_number`)
- The `fetched_at` timestamp comes from `wathq_call_logs.fetched_at`
