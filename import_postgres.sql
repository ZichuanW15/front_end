-- PostgreSQL data import for API Backbone
-- This file contains initial data for the application

-- Insert initial users
INSERT INTO "Users" (user_name, created_at, is_manager, password, email, is_deleted)
VALUES 
('Alice', '2025-09-19 13:42:09.771', true, '1234', 'alice@163.com', false),
('Alex', '2025-09-19 13:41:45.232', false, '1234', 'alex@163.com', false)
ON CONFLICT DO NOTHING;

-- Display success message
\echo '✅ Initial data imported successfully!'
\echo '   - Created 2 users (1 manager, 1 regular user)'