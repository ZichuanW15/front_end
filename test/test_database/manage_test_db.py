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
from pathlib import Path

# Set up paths and import shared utilities
from shared_utils import setup_paths, load_environment, parse_database_url, seed_test_database, clear_test_database_data, get_server_connection_params
setup_paths()

from test_utils.database_utils import create_test_database as shared_create_test_database, drop_test_database as shared_drop_test_database, setup_test_database_schema as shared_setup_schema


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


def seed_test_database_with_clear(test_db_config):
    """Seed test database with sample data, clearing existing data first."""
    clear_test_database_data(test_db_config)
    seed_test_database(test_db_config)


def show_test_database_info(main_db_config):
    """Show information about the test database."""
    test_db_name = f"{main_db_config['database']}_test"
    
    server_conn_params = get_server_connection_params(main_db_config)
    
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
    database_url, _ = load_environment()
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
        seed_test_database_with_clear(test_db_config)
    elif args.command == 'info':
        show_test_database_info(main_db_config)
    elif args.command == 'full-setup':
        # Full setup: create, setup schema, and seed
        test_db_name = create_test_database(main_db_config)
        test_db_config = main_db_config.copy()
        test_db_config['database'] = test_db_name
        setup_test_database_schema(test_db_config)
        seed_test_database_with_clear(test_db_config)
        print("\n🎉 Full test database setup completed!")
        print(f"🔗 Test database URL: postgresql://{main_db_config['user']}:***@{main_db_config['host']}:{main_db_config['port']}/{test_db_name}")


if __name__ == '__main__':
    main()