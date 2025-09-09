# Available Fractions Logic Update

## Overview
Updated the `generate.py` file to change the meaning of `available_fractions` from "unowned fractions" to "total fractions per asset".

## Changes Made

### 1. Data Generation Logic Update

**File**: `generate.py`
**Location**: Asset generation section (lines 107-110)

**Before**:
```python
# Update available_fractions per asset based on actual ownership
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

**After**:
```python
# Update available_fractions per asset - this represents total fractions per asset
# available_fractions should equal max_fractions (total fractions created for each asset)
for a in assets:
    a["available_fractions"] = a["max_fractions"]
```

### 2. Database Function Updates

**File**: `generate.py`
**Location**: Schema generation section

Updated both the `calculate_fraction_value()` function and `initialize_fraction_values()` function to use `available_fractions` instead of `max_fractions` for the calculation, since now `available_fractions` represents the total number of fractions per asset.

## Business Logic

### New Meaning of `available_fractions`:
- **Before**: Number of fractions that are not owned by anyone
- **After**: Total number of fractions that exist for each asset

### Fraction Value Calculation:
- **Formula**: `fraction_value = latest_asset_value / available_fractions`
- **Example**: 
  - Asset value: 365,332
  - Available fractions: 10,000 (total fractions per asset)
  - Fraction value: 365,332 ÷ 10,000 = 36.53

## Verification Results

### ✅ Data Generation
- All assets now have `available_fractions = max_fractions = 10,000`
- This represents the total number of fractions per asset

### ✅ Database Import
- All data imported successfully:
  - Users: 1,000
  - Assets: 100
  - Fractions: 1,000,000
  - ValueHistory: 12,000
  - Ownership: 1,000,000
  - Transactions: 50,000

### ✅ Fraction Value Calculation
- Fraction values are now calculated correctly
- Example: Asset 1 fractions have value 36.53
- Calculation: 365,332 ÷ 10,000 = 36.53

### ✅ Manager Approval Constraint
- All approved assets have managers as approvers
- Constraint working correctly

## Impact

This change makes the business logic clearer:
1. **`available_fractions`** now represents the total supply of fractions for each asset
2. **Fraction values** are calculated as the total asset value divided by the total number of fractions
3. **Ownership** is tracked separately in the Ownership table
4. **Available for purchase** fractions would be calculated as `available_fractions - owned_fractions` in application logic

The database is now ready for use with the corrected business logic.