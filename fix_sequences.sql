-- Fix sequence synchronization issues after database import
-- This script should be run after import_postgres.sql to ensure all sequences are properly synchronized

-- Fix Users sequence
SELECT setval('"Users_user_id_seq"', (SELECT MAX(user_id) FROM "Users"));

-- Fix Assets sequence  
SELECT setval('"Assets_asset_id_seq"', (SELECT MAX(asset_id) FROM "Assets"));

-- Fix Fractions sequence
SELECT setval('"Fractions_fraction_id_seq"', (SELECT MAX(fraction_id) FROM "Fractions"));

-- Fix AssetValueHistory sequence
SELECT setval('"AssetValueHistory_id_seq"', (SELECT MAX(id) FROM "AssetValueHistory"));

-- Fix Offers sequence (if any offers exist)
DO $$
DECLARE
    max_offer_id INTEGER;
BEGIN
    SELECT MAX(offer_id) INTO max_offer_id FROM "Offers";
    IF max_offer_id IS NOT NULL THEN
        PERFORM setval('"Offers_offer_id_seq"', max_offer_id);
    END IF;
END $$;

-- Fix Transactions sequence (if any transactions exist)
DO $$
DECLARE
    max_transaction_id INTEGER;
BEGIN
    SELECT MAX(transaction_id) INTO max_transaction_id FROM "Transactions";
    IF max_transaction_id IS NOT NULL THEN
        PERFORM setval('"Transactions_transaction_id_seq"', max_transaction_id);
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
SELECT 'AssetValueHistory_id_seq', last_value FROM "AssetValueHistory_id_seq"
UNION ALL
SELECT 'Offers_offer_id_seq', last_value FROM "Offers_offer_id_seq"
UNION ALL
SELECT 'Transactions_transaction_id_seq', last_value FROM "Transactions_transaction_id_seq";

\echo '✅ All sequences synchronized successfully!'
\echo '   - Users sequence fixed'
\echo '   - Assets sequence fixed' 
\echo '   - Fractions sequence fixed'
\echo '   - AssetValueHistory sequence fixed'
\echo '   - Offers sequence fixed'
\echo '   - Transactions sequence fixed'