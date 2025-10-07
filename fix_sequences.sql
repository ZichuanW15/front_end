-- Fix sequence synchronization issues after database import
-- This script should be run after import_postgres.sql to ensure all sequences are properly synchronized

-- Fix Users sequence (handle empty table case)
DO $$
DECLARE
    max_user_id INTEGER;
BEGIN
    SELECT MAX(user_id) INTO max_user_id FROM "Users";
    IF max_user_id IS NOT NULL THEN
        PERFORM setval('"Users_user_id_seq"', max_user_id);
    ELSE
        -- Initialize sequence to start from 1 (next value will be 1)
        PERFORM setval('"Users_user_id_seq"', 1, false);
    END IF;
END $$;

-- Fix Assets sequence (handle empty table case) 
DO $$
DECLARE
    max_asset_id INTEGER;
BEGIN
    SELECT MAX(asset_id) INTO max_asset_id FROM "Assets";
    IF max_asset_id IS NOT NULL THEN
        PERFORM setval('"Assets_asset_id_seq"', max_asset_id);
    ELSE
        -- Initialize sequence to start from 1 (next value will be 1)
        PERFORM setval('"Assets_asset_id_seq"', 1, false);
    END IF;
END $$;

-- Fix Fractions sequence (handle empty table case)
DO $$
DECLARE
    max_fraction_id INTEGER;
BEGIN
    SELECT MAX(fraction_id) INTO max_fraction_id FROM "Fractions";
    IF max_fraction_id IS NOT NULL THEN
        PERFORM setval('"Fractions_fraction_id_seq"', max_fraction_id);
    ELSE
        -- Initialize sequence to start from 1 (next value will be 1)
        PERFORM setval('"Fractions_fraction_id_seq"', 1, false);
    END IF;
END $$;

-- Fix AssetValueHistory sequence (only if table exists)
DO $$
DECLARE
    max_history_id INTEGER;
BEGIN
    SELECT MAX(id) INTO max_history_id FROM "AssetValueHistory";
    IF max_history_id IS NOT NULL THEN
        PERFORM setval('"AssetValueHistory_id_seq"', max_history_id);
    ELSE
        -- Initialize sequence to start from 1 (next value will be 1)
        PERFORM setval('"AssetValueHistory_id_seq"', 1, false);
    END IF;
END $$;

-- Fix Offers sequence (only if table exists)
DO $$
DECLARE
    max_offer_id INTEGER;
BEGIN
    SELECT MAX(offer_id) INTO max_offer_id FROM "Offers";
    IF max_offer_id IS NOT NULL THEN
        PERFORM setval('"Offers_offer_id_seq"', max_offer_id);
    ELSE
        -- Initialize sequence to start from 1 (next value will be 1)
        PERFORM setval('"Offers_offer_id_seq"', 1, false);
    END IF;
END $$;

-- Fix Transactions sequence (handle empty table case)
DO $$
DECLARE
    max_transaction_id INTEGER;
BEGIN
    SELECT MAX(transaction_id) INTO max_transaction_id FROM "Transactions";
    IF max_transaction_id IS NOT NULL THEN
        PERFORM setval('"Transactions_transaction_id_seq"', max_transaction_id);
    ELSE
        -- Initialize sequence to start from 1 (next value will be 1)
        PERFORM setval('"Transactions_transaction_id_seq"', 1, false);
    END IF;
END $$;

-- Display current sequence values for verification
\echo 'Current sequence values:'
SELECT 'Users_user_id_seq' as sequence_name, last_value FROM "Users_user_id_seq"
UNION ALL
SELECT 'Assets_asset_id_seq', last_value FROM "Assets_asset_id_seq"
UNION ALL
SELECT 'Fractions_fraction_id_seq', last_value FROM "Fractions_fraction_id_seq"
UNION ALL
SELECT 'Transactions_transaction_id_seq', last_value FROM "Transactions_transaction_id_seq"
UNION ALL
SELECT 'AssetValueHistory_id_seq', last_value FROM "AssetValueHistory_id_seq" WHERE EXISTS (SELECT 1 FROM pg_class WHERE relname = 'AssetValueHistory_id_seq')
UNION ALL
SELECT 'Offers_offer_id_seq', last_value FROM "Offers_offer_id_seq" WHERE EXISTS (SELECT 1 FROM pg_class WHERE relname = 'Offers_offer_id_seq');

\echo '✅ All sequences synchronized successfully!'
\echo '   - Users sequence fixed'
\echo '   - Assets sequence fixed' 
\echo '   - Fractions sequence fixed'
\echo '   - AssetValueHistory sequence fixed'
\echo '   - Offers sequence fixed'
\echo '   - Transactions sequence fixed'