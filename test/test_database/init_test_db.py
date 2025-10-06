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
from pathlib import Path

# Set up paths and import shared utilities
from shared_utils import setup_paths, load_environment, parse_database_url, seed_test_database
setup_paths()

from test_utils.database_utils import create_test_database as shared_create_test_database, setup_test_database_schema as shared_setup_schema


def create_test_database(main_db_config):
    """Create test database if it doesn't exist."""
    test_db_name = f"{main_db_config['database']}_test"
    return shared_create_test_database(main_db_config, test_db_name)


def setup_test_database_schema(test_db_config):
    """Set up the test database schema using the schema_postgres.sql file."""
    shared_setup_schema(test_db_config)




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