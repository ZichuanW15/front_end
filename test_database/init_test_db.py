#!/usr/bin/env python3
"""
Test Database Initialization Script for Provision-it project.
Creates a separate test database with the same schema, constraints, and sample data as the production database.
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from pathlib import Path


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


def create_test_database(main_db_config):
    """Create test database if it doesn't exist."""
    test_db_name = f"{main_db_config['database']}_test"
    
    # Connect to PostgreSQL server (not to specific database)
    server_conn_params = {
        'host': main_db_config['host'],
        'port': main_db_config['port'],
        'user': main_db_config['user'],
        'password': main_db_config['password'],
        'database': 'postgres'  # Connect to default postgres database
    }
    
    try:
        conn = psycopg2.connect(**server_conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (test_db_name,))
        exists = cursor.fetchone() is not None
        
        if not exists:
            print(f"📝 Creating test database: {test_db_name}")
            cursor.execute(f'CREATE DATABASE "{test_db_name}"')
            print(f"✅ Test database '{test_db_name}' created successfully")
        else:
            print(f"ℹ️  Test database '{test_db_name}' already exists")
        
        cursor.close()
        conn.close()
        
        return test_db_name
        
    except psycopg2.Error as e:
        print(f"❌ Error creating test database: {e}")
        sys.exit(1)


def setup_test_database_schema(test_db_config):
    """Set up the test database schema using the schema_postgres.sql file."""
    schema_file = Path(__file__).parent.parent / 'schema_postgres.sql'
    
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)
    
    try:
        # Connect to test database
        conn = psycopg2.connect(
            host=test_db_config['host'],
            port=test_db_config['port'],
            user=test_db_config['user'],
            password=test_db_config['password'],
            database=test_db_config['database']
        )
        
        cursor = conn.cursor()
        
        print(f"📝 Setting up schema for test database: {test_db_config['database']}")
        
        # Read and execute schema file
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Better SQL statement parsing - handle multi-line statements
        statements = []
        current_stmt = ""
        for line in schema_sql.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                current_stmt += line + " "
                if line.endswith(';'):
                    statements.append(current_stmt.strip()[:-1])  # Remove trailing semicolon
                    current_stmt = ""
        
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                except psycopg2.Error as e:
                    if "already exists" in str(e).lower():
                        print(f"⚠️  Warning: {e}")
                        continue
                    else:
                        print(f"❌ Error executing statement: {e}")
                        print(f"   Statement: {statement[:100]}...")
                        raise
        
        conn.commit()
        print("✅ Test database schema setup completed")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error setting up test database schema: {e}")
        sys.exit(1)


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


def verify_test_database_setup(test_db_config):
    """Verify that test database is properly set up."""
    try:
        conn = psycopg2.connect(
            host=test_db_config['host'],
            port=test_db_config['port'],
            user=test_db_config['user'],
            password=test_db_config['password'],
            database=test_db_config['database']
        )
        
        cursor = conn.cursor()
        
        print("🔍 Verifying test database setup...")
        
        # Check tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('Users', 'Assets', 'Fractions', 'Transactions', 'Offers', 'AssetValueHistory')
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['AssetValueHistory', 'Assets', 'Fractions', 'Offers', 'Transactions', 'Users']
        
        print(f"📋 Found tables: {tables}")
        
        if set(tables) == set(expected_tables):
            print("✅ All required tables found")
        else:
            missing = set(expected_tables) - set(tables)
            print(f"❌ Missing tables: {missing}")
            return False
        
        # Check sample data
        cursor.execute('SELECT COUNT(*) FROM "Users"')
        user_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM "Assets"')
        asset_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM "Fractions"')
        fraction_count = cursor.fetchone()[0]
        
        print(f"📊 Sample data counts:")
        print(f"   Users: {user_count}")
        print(f"   Assets: {asset_count}")
        print(f"   Fractions: {fraction_count}")
        
        if user_count > 0 and asset_count > 0 and fraction_count > 0:
            print("✅ Test database verification completed successfully")
            return True
        else:
            print("❌ Test database missing sample data")
            return False
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error verifying test database: {e}")
        return False


def main():
    """Main function to initialize test database."""
    print("🚀 Initializing test database for Provision-it project...")
    print("=" * 60)
    
    # Load environment
    database_url, test_database_url = load_environment()
    
    # Parse main database configuration
    try:
        main_db_config = parse_database_url(database_url)
        print(f"📋 Main database: {main_db_config['database']}")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Create test database
    test_db_name = create_test_database(main_db_config)
    
    # Prepare test database configuration
    test_db_config = main_db_config.copy()
    test_db_config['database'] = test_db_name
    
    # Set up schema
    setup_test_database_schema(test_db_config)
    
    # Seed with sample data
    seed_test_database(test_db_config)
    
    # Verify setup
    if verify_test_database_setup(test_db_config):
        print("\n" + "=" * 60)
        print("🎉 Test database initialization completed successfully!")
        print(f"📋 Test database: {test_db_name}")
        print(f"🔗 Connection URL: postgresql://{test_db_config['user']}:***@{test_db_config['host']}:{test_db_config['port']}/{test_db_name}")
        print("\n💡 To use this test database, set TEST_DATABASE_URL in your .env file:")
        print(f"   TEST_DATABASE_URL=postgresql://{test_db_config['user']}:{test_db_config['password']}@{test_db_config['host']}:{test_db_config['port']}/{test_db_name}")
        print("\n🧪 Run tests with: python -m pytest tests/")
    else:
        print("\n❌ Test database initialization failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()