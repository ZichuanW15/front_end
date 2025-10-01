"""
Shared database utilities to avoid code duplication.
This module provides common database connection and setup functions.
"""

import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path


def get_server_connection_params(main_db_config):
    """Get server connection parameters for database operations."""
    return {
        'host': main_db_config['host'],
        'port': main_db_config['port'],
        'user': main_db_config['user'],
        'password': main_db_config['password'],
        'database': 'postgres'
    }


def create_test_database(main_db_config, test_db_name):
    """
    Create test database with the given name.
    
    Args:
        main_db_config (dict): Main database configuration
        test_db_name (str): Name of the test database to create
        
    Returns:
        str: Name of the created test database
    """
    server_conn_params = get_server_connection_params(main_db_config)

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


def drop_test_database(main_db_config, test_db_name):
    """
    Drop test database.
    
    Args:
        main_db_config (dict): Main database configuration
        test_db_name (str): Name of the test database to drop
    """
    server_conn_params = get_server_connection_params(main_db_config)

    try:
        conn = psycopg2.connect(**server_conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if test database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (test_db_name,))
        exists = cursor.fetchone() is not None

        if exists:
            print(f"🗑️  Dropping test database: {test_db_name}")
            cursor.execute(f'DROP DATABASE "{test_db_name}"')
            print(f"✅ Test database '{test_db_name}' dropped successfully")
        else:
            print(f"ℹ️  Test database '{test_db_name}' does not exist")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"❌ Error dropping test database: {e}")
        sys.exit(1)


def setup_test_database_schema(test_db_config):
    """
    Set up the test database schema using the schema_postgres.sql file.
    Filters out psql-specific commands that can't be executed by psycopg2.
    
    Args:
        test_db_config (dict): Test database configuration
    """
    schema_file = Path(__file__).parent.parent.parent / 'schema_postgres.sql'
    
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)
    
    try:
        conn = psycopg2.connect(**test_db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"📖 Reading schema from: {schema_file}")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        # Filter out psql-specific commands that can't be executed by psycopg2
        lines = schema_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip lines that start with \ (psql-specific commands)
            if line.strip().startswith('\\'):
                continue
            filtered_lines.append(line)
        
        schema_sql = '\n'.join(filtered_lines)
        
        print("🏗️  Setting up database schema...")
        cursor.execute(schema_sql)
        print("✅ Database schema set up successfully")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error setting up database schema: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading schema file: {e}")
        sys.exit(1)


def verify_database_tables(db):
    """
    Verify that all expected tables exist in the database.
    
    Args:
        db: SQLAlchemy database instance
        
    Returns:
        bool: True if all tables exist, False otherwise
    """
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        expected_tables = ['Users', 'Assets', 'Fractions', 'Transactions', 'Offers', 'AssetValueHistory']
        missing_tables = []
        
        for table in expected_tables:
            if table not in tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            print(f"📋 Available tables: {tables}")
            return False
        
        print(f"✅ All expected tables found: {expected_tables}")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database tables: {e}")
        return False