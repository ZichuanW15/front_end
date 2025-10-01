#!/usr/bin/env python3
"""
Test Database Management Script for Provision-it project.
Provides commands to manage the test database: create, drop, reset, and seed.
"""

import os
import sys
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from pathlib import Path

# Add the project root and test directory to the Python path
project_root = Path(__file__).parent.parent.parent
test_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(test_dir))

from test_utils.database_utils import create_test_database as shared_create_test_database, drop_test_database as shared_drop_test_database, setup_test_database_schema as shared_setup_schema


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    return database_url


def parse_database_url(database_url):
    """Parse database URL into components."""
    import re
    
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


def create_test_database(main_db_config):
    """Create test database."""
    test_db_name = f"{main_db_config['database']}_test"
    return shared_create_test_database(main_db_config, test_db_name)


def drop_test_database(main_db_config):
    """Drop test database."""
    test_db_name = f"{main_db_config['database']}_test"
    shared_drop_test_database(main_db_config, test_db_name)


def reset_test_database(main_db_config):
    """Reset test database (drop and recreate)."""
    print("🔄 Resetting test database...")
    drop_test_database(main_db_config)
    create_test_database(main_db_config)
    print("✅ Test database reset completed")


def setup_test_database_schema(test_db_config):
    """Set up the test database schema."""
    shared_setup_schema(test_db_config)


def seed_test_database(test_db_config):
    """Seed test database with sample data."""
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
        
        # Clear existing data
        cursor.execute('TRUNCATE TABLE "AssetValueHistory" CASCADE')
        cursor.execute('TRUNCATE TABLE "Transactions" CASCADE')
        cursor.execute('TRUNCATE TABLE "Offers" CASCADE')
        cursor.execute('TRUNCATE TABLE "Fractions" CASCADE')
        cursor.execute('TRUNCATE TABLE "Assets" CASCADE')
        cursor.execute('TRUNCATE TABLE "Users" CASCADE')
        
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
            (asset_ids[0], user_ids[0], None, 100, True, 10.00),
            (asset_ids[0], user_ids[1], None, 50, True, 10.00),
            (asset_ids[1], user_ids[2], None, 25, True, 20.00),
            (asset_ids[2], user_ids[3], None, 10, True, 100.00)
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


def show_test_database_info(main_db_config):
    """Show information about the test database."""
    test_db_name = f"{main_db_config['database']}_test"
    
    server_conn_params = {
        'host': main_db_config['host'],
        'port': main_db_config['port'],
        'user': main_db_config['user'],
        'password': main_db_config['password'],
        'database': 'postgres'
    }
    
    try:
        conn = psycopg2.connect(**server_conn_params)
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (test_db_name,))
        exists = cursor.fetchone() is not None
        
        print(f"📋 Test Database Information:")
        print(f"   Name: {test_db_name}")
        print(f"   Status: {'✅ Exists' if exists else '❌ Does not exist'}")
        
        if exists:
            # Connect to test database to get more info
            test_conn = psycopg2.connect(
                host=main_db_config['host'],
                port=main_db_config['port'],
                user=main_db_config['user'],
                password=main_db_config['password'],
                database=test_db_name
            )
            test_cursor = test_conn.cursor()
            
            # Get table counts
            test_cursor.execute("SELECT COUNT(*) FROM \"Users\"")
            user_count = test_cursor.fetchone()[0]
            
            test_cursor.execute("SELECT COUNT(*) FROM \"Assets\"")
            asset_count = test_cursor.fetchone()[0]
            
            test_cursor.execute("SELECT COUNT(*) FROM \"Fractions\"")
            fraction_count = test_cursor.fetchone()[0]
            
            print(f"   Tables: Users({user_count}), Assets({asset_count}), Fractions({fraction_count})")
            
            test_cursor.close()
            test_conn.close()
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error getting test database info: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Manage test database for Provision-it project')
    parser.add_argument('command', choices=['create', 'drop', 'reset', 'setup', 'seed', 'info', 'full-setup'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    # Load environment
    database_url = load_environment()
    main_db_config = parse_database_url(database_url)
    
    print(f"📋 Main database: {main_db_config['database']}")
    
    if args.command == 'create':
        create_test_database(main_db_config)
    elif args.command == 'drop':
        drop_test_database(main_db_config)
    elif args.command == 'reset':
        reset_test_database(main_db_config)
    elif args.command == 'setup':
        test_db_name = f"{main_db_config['database']}_test"
        test_db_config = main_db_config.copy()
        test_db_config['database'] = test_db_name
        setup_test_database_schema(test_db_config)
    elif args.command == 'seed':
        test_db_name = f"{main_db_config['database']}_test"
        test_db_config = main_db_config.copy()
        test_db_config['database'] = test_db_name
        seed_test_database(test_db_config)
    elif args.command == 'info':
        show_test_database_info(main_db_config)
    elif args.command == 'full-setup':
        # Full setup: create, setup schema, and seed
        test_db_name = create_test_database(main_db_config)
        test_db_config = main_db_config.copy()
        test_db_config['database'] = test_db_name
        setup_test_database_schema(test_db_config)
        seed_test_database(test_db_config)
        print("\n🎉 Full test database setup completed!")
        print(f"🔗 Test database URL: postgresql://{main_db_config['user']}:***@{main_db_config['host']}:{main_db_config['port']}/{test_db_name}")


if __name__ == '__main__':
    main()