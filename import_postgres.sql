-- PostgreSQL data import for API Backbone
-- This file contains initial data for the application

-- Insert initial users
INSERT INTO "Users" (user_name, created_at, is_manager, password, email, is_deleted)
VALUES 
('Alice', '2025-09-19 13:42:09.771', true, '1234', 'alice@163.com', false),
('Alex', '2025-09-19 13:41:45.232', false, '1234', 'alex@163.com', false),
('Bob',   '2025-09-23 10:20:00', false, '1234', 'bob@example.com', false),
('Clara', '2025-09-23 10:25:00', false, '1234', 'clara@example.com', false),
('Diana', '2025-09-24 08:45:00', false, '1234', 'diana@example.com', false),
('Ethan', '2025-09-24 09:10:00', false, '1234', 'ethan@example.com', false)
ON CONFLICT DO NOTHING;

-- Insert test assets
INSERT INTO "Assets" (asset_name, total_unit, unit_min, unit_max, total_value, created_at)
VALUES 
('Modern Art Painting', 1000, 1, 100, '1000000', '2025-09-19 14:00:00'),
('Technology Equity Fund A', 500, 1, 50, '500000', '2025-09-20 10:00:00'),
('Commercial Real Estate Trust', 2000, 10, 200, '2000000', '2025-09-21 15:30:00'),
('Crypto Token', 10000, 1, 1000, '100000', '2025-09-22 09:15:00'),
('Vintage Sports Car', 100, 1, 10, '250000', '2025-09-23 11:00:00'),
('Fine Wine Collection', 300, 1, 30, '150000', '2025-09-24 09:30:00'),
('Mountain Cabin Property', 800, 5, 100, '800000', '2025-09-24 11:15:00'),
('Gold Investment Vault', 400, 1, 50, '400000', '2025-09-25 13:00:00')
ON CONFLICT DO NOTHING;

-- Insert asset value history for testing
INSERT INTO "AssetValueHistory" (asset_id, value, recorded_at, source, adjusted_by, adjustment_reason)
VALUES 
-- Modern Art Painting history
(1, 1000000.00, '2025-06-19 14:00:00', 'manual_adjust', 1, 'Initial value'),
(1, 1050000.00, '2025-07-20 09:00:00', 'manual_adjust', 1, 'Market appreciation'),
(1, 123456.78, '2025-08-24 10:26:24', 'manual_adjust', 1, 'first manual adjust'),
(1, 1300000.00, '2025-09-25 11:00:00', 'manual_adjust', 1, 'Market correction adjustment'),

-- Technology Equity Fund A history
(2, 500000.00, '2025-06-20 10:00:00', 'manual_adjust', 1, 'Initial value'),
(2, 520000.00, '2025-07-21 14:30:00', 'manual_adjust', 1, 'Tech sector growth'),
(2, 480000.00, '2025-08-22 16:45:00', 'manual_adjust', 1, 'Market volatility adjustment'),
(2, 510000.00, '2025-09-23 10:15:00', 'manual_adjust', 1, 'Recovery trend'),

-- Commercial Real Estate Trust history
(3, 2000000.00, '2025-06-21 15:30:00', 'manual_adjust', 1, 'Initial value'),
(3, 2050000.00, '2025-07-22 12:00:00', 'manual_adjust', 1, 'Property appreciation'),
(3, 2100000.00, '2025-09-23 14:20:00', 'manual_adjust', 1, 'Property revaluation'),

-- Crypto Token history
(4, 100000.00, '2025-06-22 09:15:00', 'manual_adjust', 1, 'Initial value'),
(4, 95000.00, '2025-07-23 08:30:00', 'manual_adjust', 1, 'Crypto market dip'),
(4, 110000.00, '2025-08-24 15:45:00', 'manual_adjust', 1, 'Market recovery'),
(4, 120000.00, '2025-09-25 09:30:00', 'manual_adjust', 1, 'Strategic value adjustment'),

-- added asset value history for the rest of the assets(5, 250000, '2025-09-23 11:00:00', 'manual_adjust', 1, 'Initial valuation'),
(5, 265000, '2025-09-28 10:00:00', 'manual_adjust', 1, 'Market rise'),

(6, 150000, '2025-09-24 09:30:00', 'manual_adjust', 1, 'Initial valuation'),
(6, 145000, '2025-10-02 12:00:00', 'manual_adjust', 1, 'Seasonal market drop'),

(7, 800000, '2025-09-24 11:15:00', 'manual_adjust', 1, 'Initial valuation'),
(7, 825000, '2025-10-03 11:15:00', 'manual_adjust', 1, 'Real estate appreciation'),

(8, 400000, '2025-09-25 13:00:00', 'manual_adjust', 1, 'Initial valuation'),
(8, 390000, '2025-10-01 15:00:00', 'manual_adjust', 1, 'Gold price fluctuation')
ON CONFLICT DO NOTHING;

-- Insert fractions for testing
INSERT INTO "Fractions" 
(fraction_id, asset_id, owner_id, parent_fraction_id, units, is_active, created_at, value_perunit)
VALUES
-- Asset 1: Modern Art Painting (1000 units, split between Alice and Alex)
(1, 1, 1, NULL, 600, true, '2025-09-19 14:05:00', 1000),  -- Alice
(2, 1, 2, 1,   400, true, '2025-09-19 14:06:00', 1000),  -- Alex, child of fraction 1

-- Asset 2: Technology Equity Fund (500 units, assigned to Alice only)
(3, 2, 1, NULL, 500, true, '2025-09-20 10:10:00', 1000),

-- Asset 3: Commercial Real Estate Trust (2000 units, assigned to Alex only)
(4, 3, 2, NULL, 2000, true, '2025-09-21 15:40:00', 1000),

-- Asset 4: Digital Asset Token (10000 units, assigned to Alice only)
(5, 4, 1, NULL, 10000, true, '2025-09-22 09:20:00', 10),

-- Vintage Sports Car
(6, 5, 3, NULL, 40, true, '2025-09-23 11:10:00', 2500),
(7, 5, 4, 6,   30, true, '2025-09-23 11:12:00', 2500),
(8, 5, 5, 6,   30, true, '2025-09-23 11:15:00', 2500),

-- Fine Wine Collection
(9, 6, 4, NULL, 200, true, '2025-09-24 09:40:00', 500),
(10, 6, 3, 9, 100, true, '2025-09-24 09:45:00', 500),

-- Mountain Cabin Property
(11, 7, 2, NULL, 400, true, '2025-09-24 11:30:00', 1000),
(12, 7, 5, NULL, 400, true, '2025-09-24 11:32:00', 1000),

-- Gold Investment Vault
(13, 8, 1, NULL, 200, true, '2025-09-25 13:10:00', 1000),
(14, 8, 6, NULL, 200, true, '2025-09-25 13:12:00', 1000);

-- Add offers (some buy/sell)
INSERT INTO "Offers" (offer_id, asset_id, fraction_id, user_id, is_buyer, units, create_at, price_perunit, is_valid)
VALUES
-- ✅ ACTIVE OFFERS (still open on market)
(1, 1, 1, 1, false, 100, '2025-09-26 10:00:00', 1200, true),   -- Alice selling Modern Art Painting
(2, 1, 2, 2, true, 50,  '2025-09-26 10:30:00', 1100, true),   -- Alex buying Modern Art Painting
(3, 5, 6, 3, true, 20,  '2025-09-27 09:00:00', 2600, true),   -- Bob buying Vintage Sports Car
(4, 6, 9, 4, false, 10, '2025-09-27 11:30:00', 520,  true),   -- Clara selling Fine Wine Collection
(5, 7, 11, 5, true, 50, '2025-09-28 14:00:00', 1050, true),   -- Diana buying Mountain Cabin Property
(6, 8, 14, 6, false, 30, '2025-09-29 10:00:00', 980,  true),   -- Ethan selling Gold Investment Vault

-- ❌ COMPLETED OFFERS (already executed and recorded in Transactions)
(7, 1, 1, 6, true, 100, '2025-09-27 10:00:00', 1200, true),  -- Ethan bought from Alice (Modern Art Painting)
(8, 3, 6, 3, true, 20,  '2025-09-28 10:00:00', 2600, true),  -- Bob bought from Clara (Commercial Real Estate Trust)
(9, 6, 9, 5, true, 10,  '2025-09-28 12:00:00', 520,  true),  -- Diana bought from Clara (Fine Wine)
(10, 8, 14, 1, true, 30, '2025-09-29 15:00:00', 980,  true);  -- Alice bought from Ethan (Gold Vault)
