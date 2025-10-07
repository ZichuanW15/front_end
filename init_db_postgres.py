#!/usr/bin/env python3
"""
PostgreSQL Database initialization script for Flask API Backbone.
This script uses schema_postgres.sql and import_postgres.sql files to initialize the database.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env file."""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_file):
        print(f"❌ Error: .env file not found at {env_file}")
        print("Please create a .env file with DATABASE_URL configuration.")
        sys.exit(1)
    
    load_dotenv(env_file)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        print("Please add DATABASE_URL to your .env file.")
        sys.exit(1)
    
    return database_url


def parse_database_url(database_url):
    """Parse DATABASE_URL to extract connection components."""
    try:
        # Format: postgresql://user:password@host:port/database
        if database_url.startswith('postgresql://'):
            url_part = database_url[13:]  # Remove 'postgresql://'
            
            # Split user:password from host:port/database
            if '@' in url_part:
                auth_part, host_db_part = url_part.split('@', 1)
                
                # Split user and password
                if ':' in auth_part:
                    user, password = auth_part.split(':', 1)
                else:
                    user, password = auth_part, ''
                
                # Split host:port from database
                if '/' in host_db_part:
                    host_port, database = host_db_part.split('/', 1)
                    
                    # Split host and port
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                    else:
                        host, port = host_port, '5432'
                else:
                    host, port, database = host_port, '5432', ''
            else:
                print("❌ Error: Invalid DATABASE_URL format")
                sys.exit(1)
        else:
            print("❌ Error: DATABASE_URL must start with postgresql://")
            sys.exit(1)
        
        return {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        sys.exit(1)


def check_psql_available():
    """Check if psql command is available."""
    try:
        subprocess.run(['psql', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def execute_sql_file(database_config, sql_file, description):
    """Execute a SQL file using psql."""
    if not os.path.exists(sql_file):
        print(f"❌ Error: {sql_file} not found")
        return False
    
    print(f"📋 {description}...")
    
    # Build psql command
    cmd = [
        'psql',
        '-h', database_config['host'],
        '-p', database_config['port'],
        '-U', database_config['user'],
        '-d', database_config['database'],
        '-f', sql_file
    ]
    
    try:
        # Set PGPASSWORD environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = database_config['password']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        
        print(f"✅ {description} completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing {description}: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def verify_tables_created(database_config):
    """Verify that all expected tables were created."""
    print("🔍 Verifying table creation...")
    
    cmd = [
        'psql',
        '-h', database_config['host'],
        '-p', database_config['port'],
        '-U', database_config['user'],
        '-d', database_config['database'],
        '-c', '\\dt'
    ]
    
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = database_config['password']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        
        expected_tables = ['Users', 'Assets', 'Fractions', 'Transactions', 'AssetValueHistory', 'Offers']
        output = result.stdout
        
        for table in expected_tables:
            if table in output:
                print(f"  ✅ {table} table exists")
            else:
                print(f"  ❌ {table} table missing")
                return False
        
        print("\n🎉 All tables verified successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error verifying tables: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def main():
    """Main function to initialize the database using PostgreSQL schema files."""
    print("🚀 Flask API Backbone - PostgreSQL Database Initialization")
    print("=" * 60)
    
    # Check if psql is available
    if not check_psql_available():
        print("❌ Error: psql command not found")
        print("Please install PostgreSQL client tools.")
        sys.exit(1)
    
    # Load environment variables
    database_url = load_environment()
    database_config = parse_database_url(database_url)
    
    print(f"📡 Using database: {database_config['host']}:{database_config['port']}/{database_config['database']}")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_file = os.path.join(script_dir, 'schema_postgres.sql')
    import_file = os.path.join(script_dir, 'import_postgres.sql')
    fix_sequences_file = os.path.join(script_dir, 'fix_sequences.sql')
    
    # Execute schema creation
    if not execute_sql_file(database_config, schema_file, "Creating database schema"):
        print("\n❌ Database schema creation failed!")
        sys.exit(1)
    
    # Execute data import
    if not execute_sql_file(database_config, import_file, "Importing initial data"):
        print("\n❌ Data import failed!")
        sys.exit(1)

    # Fix sequence synchronization issues
    if not execute_sql_file(database_config, fix_sequences_file, "Fixing sequence synchronization"):
        print("\n❌ Sequence synchronization failed!")
        sys.exit(1)
    
    # Verify tables were created
    if not verify_tables_created(database_config):
        print("\n❌ Table verification failed!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎯 PostgreSQL database initialization completed successfully!")
    print("\n📝 Next steps:")
    print("  1. Your database is ready with the new schema")
    print("  2. Start your Flask application")
    print("  3. Test the endpoints")
    print(f"  4. Health check: http://localhost:5001/health")


if __name__ == "__main__":
    main()