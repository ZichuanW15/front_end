-- PostgreSQL data import for API Backbone
-- This file contains initial data for the application

-- Insert initial users
INSERT INTO "Users" (user_name, created_at, is_manager, password, email, is_deleted)
VALUES 
('Alice', '2025-09-19 13:42:09.771', true, '1234', 'alice@163.com', false),
('Alex', '2025-09-19 13:41:45.232', false, '1234', 'alex@163.com', false)
ON CONFLICT DO NOTHING;

-- Insert test assets
INSERT INTO "Assets" (asset_name, total_unit, unit_min, unit_max, total_value, created_at)
VALUES 
('Modern Art Painting', 1000, 1, 100, '1000000', '2025-09-19 14:00:00'),
('Technology Equity Fund A', 500, 1, 50, '500000', '2025-09-20 10:00:00'),
('Commercial Real Estate Trust', 2000, 10, 200, '2000000', '2025-09-21 15:30:00'),
('Crypto Token', 10000, 1, 1000, '100000', '2025-09-22 09:15:00')
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
(4, 120000.00, '2025-09-25 09:30:00', 'manual_adjust', 1, 'Strategic value adjustment')
ON CONFLICT DO NOTHING;

-- Display success message
\echo '✅ Initial data imported successfully!'
\echo '   - Created 2 users (1 manager, 1 regular user)'
\echo '   - Created 4 test assets with value history'
\echo '   - Added 13 asset value history records for testing'