# Database Modifications Summary

## Overview
This document summarizes the modifications made to the PostgreSQL database schema to implement the following requirements:

1. **Manager Approval Constraint**: Only users with `is_manager = 1` can approve submitted assets
2. **Dynamic Fraction Value Calculation**: Fraction values are calculated from the latest ValueHistory entry divided by available fractions

## Changes Made

### 1. Manager Approval Constraint

**File**: `schema_postgres.sql`
**Location**: Assets table definition

Added a CHECK constraint to the Assets table to ensure only managers can approve assets:

```sql
CONSTRAINT check_manager_approval CHECK (
  approved_by_Users_user_id IS NULL OR 
  EXISTS (SELECT 1 FROM Users WHERE user_id = approved_by_Users_user_id AND is_manager = TRUE)
)
```

**How it works**:
- The constraint allows `approved_by_Users_user_id` to be NULL (for unapproved assets)
- If a user ID is provided, it must exist in the Users table with `is_manager = TRUE`
- This prevents non-manager users from being assigned as approvers

### 2. Dynamic Fraction Value Calculation

**File**: `schema_postgres.sql`
**Components Added**:

#### A. Calculation Function
```sql
CREATE OR REPLACE FUNCTION calculate_fraction_value(asset_id INTEGER)
RETURNS NUMERIC(12,2)
```

**Purpose**: Calculates the value of a fraction by:
1. Getting the latest asset value from ValueHistory (ordered by update_time DESC)
2. Getting the available_fractions from the Assets table
3. Dividing the latest value by available fractions
4. Returning 0 if no data is available

#### B. Automatic Update Triggers

**ValueHistory Trigger**:
```sql
CREATE TRIGGER trigger_update_fraction_values
    AFTER INSERT OR UPDATE ON ValueHistory
    FOR EACH ROW
    EXECUTE FUNCTION update_fraction_values();
```

**Assets Trigger**:
```sql
CREATE TRIGGER trigger_update_fraction_values_on_asset_change
    AFTER UPDATE OF available_fractions ON Assets
    FOR EACH ROW
    EXECUTE FUNCTION update_fraction_values_on_asset_change();
```

**Purpose**: Automatically recalculate all fraction values when:
- New value history entries are added or updated
- Available fractions count changes for an asset

#### C. Initialization Function
```sql
CREATE OR REPLACE FUNCTION initialize_fraction_values()
RETURNS VOID
```

**Purpose**: Updates all existing fraction values with calculated values based on current data.

### 3. Import Script Updates

**File**: `import_postgres.sql`

Added initialization call after data import:
```sql
SELECT initialize_fraction_values();
```

**Purpose**: Ensures that after importing existing data, all fraction values are properly calculated based on the latest ValueHistory entries.

## Database Behavior

### Manager Approval
- When inserting/updating an asset with an approver, the system will automatically validate that the approver is a manager
- Non-manager users cannot be assigned as approvers
- Assets can still be created without an approver (NULL values allowed)

### Fraction Value Calculation
- Fraction values are automatically calculated and updated in real-time
- When a new value history entry is added, all fractions for that asset are recalculated
- When available fractions change for an asset, all fractions for that asset are recalculated
- The calculation uses the most recent value history entry (by timestamp)
- Formula: `fraction_value = latest_asset_value / available_fractions`

## Usage Examples

### Checking Manager Status
```sql
-- Find all managers
SELECT user_id, username, email FROM Users WHERE is_manager = TRUE;

-- Check if a user can approve assets
SELECT is_manager FROM Users WHERE user_id = 123;
```

### Calculating Fraction Values
```sql
-- Get current fraction value for a specific fraction
SELECT fraction_id, fraction_value, 
       calculate_fraction_value(Assets_asset_id) as calculated_value
FROM Fractions WHERE fraction_id = 1;

-- Manually recalculate all fraction values
SELECT initialize_fraction_values();
```

### Asset Approval
```sql
-- Approve an asset (only works if user is a manager)
UPDATE Assets 
SET status = 'approved', 
    approved_by_Users_user_id = 123, 
    approved_at = NOW()
WHERE asset_id = 1;
```

## Data Integrity

The modifications ensure:
1. **Referential Integrity**: Only valid manager users can approve assets
2. **Data Consistency**: Fraction values are always up-to-date with the latest asset valuations
3. **Automatic Maintenance**: No manual intervention required to keep fraction values current
4. **Backward Compatibility**: Existing data is preserved and properly initialized

## Performance Considerations

- Indexes are maintained on key lookup columns
- Triggers only fire on relevant changes (ValueHistory updates, available_fractions changes)
- The calculation function is optimized to use the latest value efficiently
- Fraction value updates are batched per asset to minimize overhead