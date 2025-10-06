-- Improved sequence synchronization script that handles gaps properly
-- This script should be run after database operations to ensure all sequences are properly synchronized

-- Function to fix a sequence by filling gaps
CREATE OR REPLACE FUNCTION fix_sequence_with_gaps(sequence_name TEXT, table_name TEXT, id_column TEXT)
RETURNS INTEGER AS $$
DECLARE
    next_available_id INTEGER;
    max_existing_id INTEGER;
BEGIN
    -- Get all existing IDs
    EXECUTE format('SELECT COALESCE(MAX(%I), 0) FROM %I', id_column, table_name) INTO max_existing_id;
    
    -- If no records exist, start from 1
    IF max_existing_id = 0 THEN
        PERFORM setval(sequence_name, 0);
        RETURN 1;
    END IF;
    
    -- Find the next available ID by checking for gaps
    next_available_id := 1;
    
    WHILE next_available_id <= max_existing_id + 1 LOOP
        -- Check if this ID exists
        EXECUTE format('SELECT NOT EXISTS (SELECT 1 FROM %I WHERE %I = %s)', 
                      table_name, id_column, next_available_id) INTO EXISTS;
        
        IF EXISTS THEN
            -- Found a gap or the next number after max
            EXIT;
        END IF;
        next_available_id := next_available_id + 1;
    END LOOP;
    
    -- Set the sequence to the next available ID - 1
    PERFORM setval(sequence_name, next_available_id - 1);
    
    RETURN next_available_id;
END;
$$ LANGUAGE plpgsql;

-- Fix all sequences using the improved function
DO $$
DECLARE
    next_id INTEGER;
BEGIN
    -- Fix Fractions sequence
    SELECT fix_sequence_with_gaps('"Fractions_fraction_id_seq"', '"Fractions"', 'fraction_id') INTO next_id;
    RAISE NOTICE 'Fractions sequence fixed. Next ID will be: %', next_id;
    
    -- Fix Users sequence
    SELECT fix_sequence_with_gaps('"Users_user_id_seq"', '"Users"', 'user_id') INTO next_id;
    RAISE NOTICE 'Users sequence fixed. Next ID will be: %', next_id;
    
    -- Fix Assets sequence
    SELECT fix_sequence_with_gaps('"Assets_asset_id_seq"', '"Assets"', 'asset_id') INTO next_id;
    RAISE NOTICE 'Assets sequence fixed. Next ID will be: %', next_id;
    
    -- Fix Offers sequence
    SELECT fix_sequence_with_gaps('"Offers_offer_id_seq"', '"Offers"', 'offer_id') INTO next_id;
    RAISE NOTICE 'Offers sequence fixed. Next ID will be: %', next_id;
    
    -- Fix Transactions sequence
    SELECT fix_sequence_with_gaps('"Transactions_transaction_id_seq"', '"Transactions"', 'transaction_id') INTO next_id;
    RAISE NOTICE 'Transactions sequence fixed. Next ID will be: %', next_id;
    
    -- Fix AssetValueHistory sequence
    SELECT fix_sequence_with_gaps('"AssetValueHistory_id_seq"', '"AssetValueHistory"', 'id') INTO next_id;
    RAISE NOTICE 'AssetValueHistory sequence fixed. Next ID will be: %', next_id;
END $$;

-- Display current sequence values for verification
SELECT 'Sequence Status' as info, '' as value
UNION ALL
SELECT 'Fractions sequence', last_value::text FROM "Fractions_fraction_id_seq"
UNION ALL
SELECT 'Users sequence', last_value::text FROM "Users_user_id_seq"
UNION ALL
SELECT 'Assets sequence', last_value::text FROM "Assets_asset_id_seq"
UNION ALL
SELECT 'Offers sequence', last_value::text FROM "Offers_offer_id_seq"
UNION ALL
SELECT 'Transactions sequence', last_value::text FROM "Transactions_transaction_id_seq"
UNION ALL
SELECT 'AssetValueHistory sequence', last_value::text FROM "AssetValueHistory_id_seq";

-- Clean up the helper function
DROP FUNCTION IF EXISTS fix_sequence_with_gaps(TEXT, TEXT, TEXT);

\echo '✅ All sequences synchronized with gap-filling!'
\echo '   - New records will use the next available ID (filling gaps)'
\echo '   - Sequences are properly synchronized with existing data'
