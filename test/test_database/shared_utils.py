#!/usr/bin/env python3
"""
Shared utilities for test database management.
Contains common functions to eliminate code duplication.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from pathlib import Path


def setup_paths():
    """Set up Python paths for test database scripts."""
    project_root = Path(__file__).parent.parent.parent
    test_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(test_dir))


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    # Get database configuration
    database_url = os.environ.get('DATABASE_URL')
    test_database_url = os.environ.get('TEST_DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    return database_url, test_database_url


def parse_database_url(database_url):
    """Parse database URL into components."""
    import re
    
    # Parse postgresql://user:password@host:port/database
    pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, database_url)
    
    if not match:
        raise ValueError(f"Invalid database URL format: {database_url}")
    
    user, password, host, port, database = match.groups()
    
    return {
        'user': user,
        'password': password,
        'host': host,
        'port': int(port),
        'database': database
    }


def seed_test_database(test_db_config):
    """Seed test database with sample data for testing."""
    try:
        conn = psycopg2.connect(
            host=test_db_config['host'],
            port=test_db_config['port'],
            user=test_db_config['user'],
            password=test_db_config['password'],
            database=test_db_config['database']
        )
        
        cursor = conn.cursor()
        
        print("📝 Seeding test database with sample data...")
        
        # Insert sample users (without specifying user_id since it's GENERATED ALWAYS)
        users_data = [
            ('admin', 'admin@test.com', 'admin123', True),
            ('testuser1', 'user1@test.com', 'password123', False),
            ('testuser2', 'user2@test.com', 'password123', False),
            ('manager1', 'manager@test.com', 'manager123', True)
        ]
        
        user_ids = []
        for username, email, password, is_manager in users_data:
            cursor.execute("""
                INSERT INTO "Users" (user_name, email, password, is_manager, created_at, is_deleted)
                VALUES (%s, %s, %s, %s, NOW(), FALSE)
                RETURNING user_id
            """, (username, email, password, is_manager))
            user_ids.append(cursor.fetchone()[0])
        
        # Insert sample assets (without specifying asset_id since it's GENERATED ALWAYS)
        assets_data = [
            ('Test Asset 1', 'Description for test asset 1', 1000, 1, 100, 10000.00),
            ('Test Asset 2', 'Description for test asset 2', 500, 1, 50, 5000.00),
            ('Test Asset 3', 'Description for test asset 3', 200, 1, 20, 2000.00)
        ]
        
        asset_ids = []
        for name, description, total_unit, unit_min, unit_max, total_value in assets_data:
            cursor.execute("""
                INSERT INTO "Assets" (asset_name, asset_description, total_unit, unit_min, unit_max, total_value, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                RETURNING asset_id
            """, (name, description, total_unit, unit_min, unit_max, total_value))
            asset_ids.append(cursor.fetchone()[0])
        
        # Insert sample fractions (using actual user_ids and asset_ids from above)
        fractions_data = [
            (asset_ids[0], user_ids[0], None, 100, True, 10.00),  # Admin owns 100 units of Asset 1
            (asset_ids[0], user_ids[1], None, 50, True, 10.00),   # User1 owns 50 units of Asset 1
            (asset_ids[1], user_ids[2], None, 25, True, 20.00),   # User2 owns 25 units of Asset 2
            (asset_ids[2], user_ids[3], None, 10, True, 100.00)  # Manager1 owns 10 units of Asset 3
        ]
        
        for asset_id, owner_id, parent_id, units, is_active, value_per_unit in fractions_data:
            cursor.execute("""
                INSERT INTO "Fractions" (asset_id, owner_id, parent_fraction_id, units, is_active, created_at, value_perunit)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            """, (asset_id, owner_id, parent_id, units, is_active, value_per_unit))
        
        # Insert sample asset value history (using actual asset_ids)
        value_history_data = [
            (asset_ids[0], 10.00, 'system', None, 'Initial value'),
            (asset_ids[0], 12.00, 'admin', user_ids[0], 'Value adjustment'),
            (asset_ids[1], 20.00, 'system', None, 'Initial value'),
            (asset_ids[2], 100.00, 'system', None, 'Initial value')
        ]
        
        for asset_id, value, source, adjusted_by, reason in value_history_data:
            cursor.execute("""
                INSERT INTO "AssetValueHistory" (asset_id, value, recorded_at, source, adjusted_by, adjustment_reason)
                VALUES (%s, %s, NOW(), %s, %s, %s)
            """, (asset_id, value, source, adjusted_by, reason))
        
        conn.commit()
        print("✅ Test database seeded with sample data")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error seeding test database: {e}")
        sys.exit(1)


def clear_test_database_data(test_db_config):
    """Clear all data from test database tables."""
    try:
        conn = psycopg2.connect(
            host=test_db_config['host'],
            port=test_db_config['port'],
            user=test_db_config['user'],
            password=test_db_config['password'],
            database=test_db_config['database']
        )
        
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('TRUNCATE TABLE "AssetValueHistory" CASCADE')
        cursor.execute('TRUNCATE TABLE "Transactions" CASCADE')
        cursor.execute('TRUNCATE TABLE "Offers" CASCADE')
        cursor.execute('TRUNCATE TABLE "Fractions" CASCADE')
        cursor.execute('TRUNCATE TABLE "Assets" CASCADE')
        cursor.execute('TRUNCATE TABLE "Users" CASCADE')
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error clearing test database: {e}")
        sys.exit(1)