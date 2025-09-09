-- =====================================================
-- PostgreSQL Database Validation Test Suite
-- Fractional Ownership Asset Management System
-- =====================================================

-- Test Environment Setup
\echo 'Starting Database Validation Tests...'
\echo '====================================='

-- =====================================================
-- TC01: Correct fraction value calculation
-- =====================================================
\echo ''
\echo 'TC01: Testing fraction value calculation...'
\echo 'Purpose: Verify that fraction_value = latest_asset_value / available_fractions'

WITH fraction_calculations AS (
    SELECT 
        f.fraction_id,
        f.Assets_asset_id,
        f.fraction_value as actual_value,
        ROUND(
            (SELECT vh.asset_value 
             FROM ValueHistory vh 
             WHERE vh.Assets_asset_id = f.Assets_asset_id 
             ORDER BY vh.update_time DESC 
             LIMIT 1)::NUMERIC(12,2) / 
            (SELECT a.available_fractions 
             FROM Assets a 
             WHERE a.asset_id = f.Assets_asset_id), 2
        ) as expected_value
    FROM Fractions f
    WHERE f.Assets_asset_id IN (1, 2, 3, 4, 5)  -- Test first 5 assets
)
SELECT 
    COUNT(*) as total_fractions_tested,
    COUNT(CASE WHEN actual_value = expected_value THEN 1 END) as correct_calculations,
    COUNT(CASE WHEN actual_value != expected_value THEN 1 END) as incorrect_calculations
FROM fraction_calculations;

-- Expected: All calculations should be correct (incorrect_calculations = 0)

-- =====================================================
-- TC02: All assets have exactly 10,000 available_fractions
-- =====================================================
\echo ''
\echo 'TC02: Testing available_fractions = 10,000 for all assets...'
\echo 'Purpose: Validate that all assets have exactly 10,000 available fractions'

SELECT 
    COUNT(*) as total_assets,
    COUNT(CASE WHEN available_fractions = 10000 THEN 1 END) as assets_with_10000_fractions,
    COUNT(CASE WHEN available_fractions != 10000 THEN 1 END) as assets_with_wrong_fractions,
    MIN(available_fractions) as min_fractions,
    MAX(available_fractions) as max_fractions
FROM Assets;

-- Expected: assets_with_wrong_fractions = 0, min_fractions = 10000, max_fractions = 10000

-- =====================================================
-- TC03: Manager approval constraint
-- =====================================================
\echo ''
\echo 'TC03: Testing manager approval constraint...'
\echo 'Purpose: Ensure all approved assets are approved by managers only'

-- Test 1: All non-null approvers are managers
SELECT 
    COUNT(*) as total_approved_assets,
    COUNT(CASE WHEN u.is_manager = TRUE THEN 1 END) as approved_by_managers,
    COUNT(CASE WHEN u.is_manager = FALSE OR u.is_manager IS NULL THEN 1 END) as approved_by_non_managers
FROM Assets a
JOIN Users u ON a.approved_by_Users_user_id = u.user_id
WHERE a.approved_by_Users_user_id IS NOT NULL;

-- Expected: approved_by_non_managers = 0

-- Test 2: Check for any non-manager approvers
SELECT 
    a.asset_id,
    a.approved_by_Users_user_id,
    u.is_manager
FROM Assets a
JOIN Users u ON a.approved_by_Users_user_id = u.user_id
WHERE a.approved_by_Users_user_id IS NOT NULL 
  AND u.is_manager = FALSE;

-- Expected: 0 rows returned

-- =====================================================
-- TC04: Ownership integrity
-- =====================================================
\echo ''
\echo 'TC04: Testing ownership integrity...'
\echo 'Purpose: Verify ownership data integrity and no duplicates'

-- Test 1: All ownership fraction_ids exist in Fractions table
SELECT 
    COUNT(*) as total_ownership_records,
    COUNT(CASE WHEN f.fraction_id IS NOT NULL THEN 1 END) as valid_fraction_references,
    COUNT(CASE WHEN f.fraction_id IS NULL THEN 1 END) as invalid_fraction_references
FROM Ownership o
LEFT JOIN Fractions f ON o.Fractions_fraction_id = f.fraction_id;

-- Expected: invalid_fraction_references = 0

-- Test 2: No duplicate (user_id, fraction_id) pairs
SELECT 
    Users_user_id,
    Fractions_fraction_id,
    COUNT(*) as duplicate_count
FROM Ownership
GROUP BY Users_user_id, Fractions_fraction_id
HAVING COUNT(*) > 1
LIMIT 10;

-- Expected: 0 rows returned

-- Test 3: Verify all fractions are owned (since generate.py assigns all fractions)
SELECT 
    (SELECT COUNT(*) FROM Fractions) as total_fractions,
    (SELECT COUNT(*) FROM Ownership) as total_ownership_records,
    (SELECT COUNT(*) FROM Fractions) - (SELECT COUNT(*) FROM Ownership) as unowned_fractions;

-- Expected: unowned_fractions = 0 (all fractions should be owned)

-- =====================================================
-- TC05: Asset valuation exists
-- =====================================================
\echo ''
\echo 'TC05: Testing asset valuation existence...'
\echo 'Purpose: Check that every asset has at least one entry in ValueHistory'

-- Test 1: Assets without ValueHistory entries
SELECT 
    a.asset_id,
    a.name
FROM Assets a
LEFT JOIN ValueHistory vh ON a.asset_id = vh.Assets_asset_id
WHERE vh.Assets_asset_id IS NULL;

-- Expected: 0 rows returned

-- Test 2: Count of ValueHistory entries per asset
SELECT 
    COUNT(DISTINCT a.asset_id) as total_assets,
    COUNT(DISTINCT vh.Assets_asset_id) as assets_with_value_history,
    COUNT(DISTINCT a.asset_id) - COUNT(DISTINCT vh.Assets_asset_id) as assets_without_value_history
FROM Assets a
LEFT JOIN ValueHistory vh ON a.asset_id = vh.Assets_asset_id;

-- Expected: assets_without_value_history = 0

-- Test 3: Verify expected number of ValueHistory entries (120 days per asset)
SELECT 
    COUNT(*) as total_value_history_entries,
    COUNT(DISTINCT Assets_asset_id) as assets_with_history,
    COUNT(*) / COUNT(DISTINCT Assets_asset_id) as avg_entries_per_asset
FROM ValueHistory;

-- Expected: avg_entries_per_asset should be close to 120

-- =====================================================
-- TC06: Available fractions ≠ unowned fractions
-- =====================================================
\echo ''
\echo 'TC06: Testing available_fractions independence from ownership...'
\echo 'Purpose: Confirm available_fractions is constant and independent of ownership'

-- Test 1: Verify available_fractions is constant across all assets
SELECT 
    COUNT(DISTINCT available_fractions) as distinct_available_fractions_values,
    MIN(available_fractions) as min_available,
    MAX(available_fractions) as max_available
FROM Assets;

-- Expected: distinct_available_fractions_values = 1, min_available = 10000, max_available = 10000

-- Test 2: Verify available_fractions = max_fractions for all assets
SELECT 
    COUNT(*) as total_assets,
    COUNT(CASE WHEN available_fractions = max_fractions THEN 1 END) as matching_values,
    COUNT(CASE WHEN available_fractions != max_fractions THEN 1 END) as non_matching_values
FROM Assets;

-- Expected: non_matching_values = 0

-- Test 3: Sample check - show that available_fractions doesn't change based on ownership
SELECT 
    a.asset_id,
    a.available_fractions,
    a.max_fractions,
    COUNT(o.Fractions_fraction_id) as owned_fractions_count,
    a.available_fractions - COUNT(o.Fractions_fraction_id) as difference
FROM Assets a
LEFT JOIN Ownership o ON a.asset_id = o.Fractions_Assets_asset_id
GROUP BY a.asset_id, a.available_fractions, a.max_fractions
ORDER BY a.asset_id
LIMIT 5;

-- Expected: difference should be 0 (all fractions are owned, but available_fractions = max_fractions)

-- =====================================================
-- Additional Validation Tests
-- =====================================================
\echo ''
\echo 'Additional Validation Tests...'
\echo '=============================='

-- Test 7: Data volume validation
\echo ''
\echo 'TC07: Data volume validation...'
SELECT 
    'Users' as table_name, COUNT(*) as record_count FROM Users
UNION ALL
SELECT 'Assets', COUNT(*) FROM Assets
UNION ALL
SELECT 'Fractions', COUNT(*) FROM Fractions
UNION ALL
SELECT 'Ownership', COUNT(*) FROM Ownership
UNION ALL
SELECT 'Transactions', COUNT(*) FROM Transactions
UNION ALL
SELECT 'ValueHistory', COUNT(*) FROM ValueHistory;

-- Test 8: Fraction distribution per asset
\echo ''
\echo 'TC08: Fraction distribution validation...'
SELECT 
    COUNT(DISTINCT Assets_asset_id) as total_assets,
    COUNT(*) / COUNT(DISTINCT Assets_asset_id) as avg_fractions_per_asset,
    MIN(fraction_count) as min_fractions_per_asset,
    MAX(fraction_count) as max_fractions_per_asset
FROM (
    SELECT Assets_asset_id, COUNT(*) as fraction_count
    FROM Fractions
    GROUP BY Assets_asset_id
) fraction_counts;

-- Expected: avg_fractions_per_asset = 10000, min_fractions_per_asset = 10000, max_fractions_per_asset = 10000

-- Test 9: ValueHistory time range validation
\echo ''
\echo 'TC09: ValueHistory time range validation...'
SELECT 
    MIN(update_time) as earliest_value_date,
    MAX(update_time) as latest_value_date,
    MAX(update_time) - MIN(update_time) as time_span_days
FROM ValueHistory;

-- Expected: time_span_days should be approximately 120 days

-- =====================================================
-- Test Summary
-- =====================================================
\echo ''
\echo '====================================='
\echo 'Test Suite Execution Complete'
\echo '====================================='
\echo 'Review the results above to ensure all tests pass.'
\echo 'Key expectations:'
\echo '- TC01: All fraction calculations should be correct'
\echo '- TC02: All assets should have exactly 10,000 available_fractions'
\echo '- TC03: All approvers should be managers'
\echo '- TC04: All ownership records should be valid with no duplicates'
\echo '- TC05: All assets should have ValueHistory entries'
\echo '- TC06: available_fractions should be constant and independent of ownership'
\echo '====================================='