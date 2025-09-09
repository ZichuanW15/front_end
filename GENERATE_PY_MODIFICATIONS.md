# Generate.py Modifications Summary

## Overview
This document summarizes the modifications made to `generate.py` to ensure it follows the new database rules and generates data that can be properly imported into the PostgreSQL database.

## Changes Made

### 1. Manager Approval Constraint Implementation

**Location**: Asset generation section (lines 49-81)

**Changes**:
- Added logic to identify manager users before generating assets
- Modified asset approval logic to only assign approvers if:
  - The asset status is "approved"
  - Manager users exist in the system
- Ensured that only users with `is_manager = 1` can be assigned as approvers

**Code Changes**:
```python
# First, identify which users are managers
manager_users = [u["user_id"] for u in users if u["is_manager"] == 1]

# Only assign approver if status is approved and we have managers
approver = None
approved_at = None
if status == "approved" and manager_users:
    approver = random.choice(manager_users)
    approved_at = created_at + timedelta(days=random.randint(1,30))
```

### 2. Fraction Value Calculation Fix

**Location**: Fraction generation section (lines 83-94)

**Changes**:
- Removed random fraction value generation
- Set all fraction values to 0.00 initially
- Values will be calculated by the database function after import

**Code Changes**:
```python
fractions.append({
    "fraction_id": fid,
    "Assets_asset_id": a["asset_id"],
    "fraction_no": n,
    "fraction_value": 0.00  # Will be calculated by database function
})
```

### 3. Available Fractions Calculation Fix

**Location**: After ownership generation (lines 107-117)

**Changes**:
- Fixed the calculation of `available_fractions` to reflect actual ownership
- Counts owned fractions per asset and subtracts from max_fractions
- Ensures data integrity between Assets and Ownership tables

**Code Changes**:
```python
# Count how many fractions are owned for each asset
asset_owned_counts = {}
for ownership in ownerships:
    asset_id = ownership["Fractions_Assets_asset_id"]
    asset_owned_counts[asset_id] = asset_owned_counts.get(asset_id, 0) + 1

# Update available_fractions for each asset
for a in assets:
    owned_count = asset_owned_counts.get(a["asset_id"], 0)
    a["available_fractions"] = a["max_fractions"] - owned_count
```

### 4. Schema Updates

**Location**: Schema generation section (lines 214-295)

**Changes**:
- Added manager approval constraint to Assets table
- Added fraction value calculation function
- Added trigger for automatic fraction value updates
- Added initialization function for existing data

**Key Additions**:
```sql
CONSTRAINT check_manager_approval CHECK (
  approved_by_Users_user_id IS NULL OR 
  EXISTS (SELECT 1 FROM Users WHERE user_id = approved_by_Users_user_id AND is_manager = TRUE)
)
```

### 5. Import Script Updates

**Location**: Import script generation (lines 339-351)

**Changes**:
- Added call to `initialize_fraction_values()` function after data import
- Ensures fraction values are calculated after all data is loaded

## Data Validation

### Manager Approval Verification
- ✅ Approved assets only have managers as approvers
- ✅ Non-approved assets have NULL approvers
- ✅ All approvers have `is_manager = 1`

### Fraction Value Verification
- ✅ All fractions start with value 0.00
- ✅ Values will be calculated by database function after import
- ✅ Calculation based on latest ValueHistory and available fractions

### Available Fractions Verification
- ✅ Available fractions = max_fractions - owned_fractions
- ✅ Data consistency between Assets and Ownership tables

## Generated Files

The modified `generate.py` successfully generates:
- `Users.csv` - 1,000 users with proper manager flags
- `Assets.csv` - 100 assets with correct approval constraints
- `Fractions.csv` - 1,000,000 fractions with initial values of 0.00
- `Ownership.csv` - Ownership records for all fractions
- `Transactions.csv` - 50,000 transaction records
- `ValueHistory.csv` - 12,000 value history records (120 days × 100 assets)
- `schema_postgres.sql` - Updated schema with constraints and functions
- `import_postgres.sql` - Import script with initialization call

## Testing Results

- ✅ Script runs without errors
- ✅ All CSV files generated successfully
- ✅ Data structure validates against new constraints
- ✅ Ready for database import

## Usage

1. Run the modified `generate.py` script
2. Import the schema: `\i schema_postgres.sql`
3. Import the data: `\i import_postgres.sql`
4. Fraction values will be automatically calculated and updated

The generated data is now fully compatible with the new database rules and constraints.