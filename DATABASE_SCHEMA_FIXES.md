# Database Schema Fixes

## Issue

When running `python test/test_database/manage_test_db.py full-setup`, the following error occurred:

```
❌ Error seeding test database: column "asset_description" of relation "Assets" does not exist
LINE 2:                 INSERT INTO "Assets" (asset_name, asset_desc...
```

## Root Cause

There were mismatches between the SQLAlchemy models (`app/models.py`) and the PostgreSQL schema (`schema_postgres.sql`).

## Fixes Applied

### 1. Added Missing `asset_description` Column ✅

**File**: `schema_postgres.sql`

**Before** (line 33-41):
```sql
CREATE TABLE "Assets" (
  asset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  asset_name TEXT NOT NULL,
  total_unit BIGINT NOT NULL,
  unit_min BIGINT NOT NULL,
  unit_max BIGINT NOT NULL,
  total_value NUMERIC(18,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

**After**:
```sql
CREATE TABLE "Assets" (
  asset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  asset_name TEXT NOT NULL,
  asset_description TEXT,           -- ← ADDED
  total_unit BIGINT NOT NULL,
  unit_min BIGINT NOT NULL,
  unit_max BIGINT NOT NULL,
  total_value NUMERIC(18,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

### 2. Fixed `total_value` Type in Asset Model ✅

**File**: `app/models.py`

**Before** (line 58):
```python
total_value = Column(String, nullable=False)
```

**After**:
```python
total_value = Column(Numeric(18, 2), nullable=False)
```

**Reason**: The SQL schema uses `NUMERIC(18,2)` but the model used `String`, causing potential type conversion issues.

### 3. Fixed `value_perunit` Type in Fraction Model ✅

**File**: `app/models.py`

**Before** (line 92):
```python
value_perunit = Column(BigInteger)
```

**After**:
```python
value_perunit = Column(Numeric(18, 2), nullable=False)
```

**Reason**: The SQL schema uses `NUMERIC(18,2) NOT NULL` but the model used `BigInteger`, which would truncate decimal values.

## Impact

These fixes ensure:
- ✅ The seed function can successfully insert test data with descriptions
- ✅ Asset and fraction values are stored with proper decimal precision
- ✅ SQLAlchemy models match the PostgreSQL schema exactly
- ✅ Type conversions work correctly between Python and PostgreSQL

## Testing

Run the full test database setup again:

```bash
python test/test_database/manage_test_db.py full-setup
```

Expected output:
```
📋 Main database: provision_it_v2
📝 Creating test database: provision_it_v2_test
✅ Test database 'provision_it_v2_test' created successfully
📖 Reading schema from: /path/to/schema_postgres.sql
🏗️  Setting up database schema...
✅ Database schema set up successfully
📝 Seeding test database with sample data...
✅ Test database seeded with sample data

🎉 Full test database setup completed!
```

## Files Modified

1. ✅ `schema_postgres.sql` - Added `asset_description` column
2. ✅ `app/models.py` - Fixed `total_value` and `value_perunit` types

## Summary

All database schema mismatches have been resolved. The SQLAlchemy models and PostgreSQL schema are now in sync, allowing proper test database setup and data seeding.

