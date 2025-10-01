"""
Test database setup utilities.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def setup_test_database():
    """Set up test database using the full setup script."""
    script_path = Path(__file__).parent / 'init_test_db.py'
    
    print("🔧 Setting up test database...")
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              check=True, capture_output=True, text=True)
        print("✅ Test database setup completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test database setup failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def setup_test_database_schema():
    """Set up test database schema using Flask app."""
    script_path = Path(__file__).parent / 'setup_schema.py'
    
    print("🔧 Setting up test database schema...")
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              check=True, capture_output=True, text=True)
        print("✅ Test database schema setup completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test database schema setup failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def ensure_test_database_exists():
    """Ensure test database exists, create if it doesn't."""
    script_path = Path(__file__).parent / 'manage_test_db.py'
    
    try:
        # Check if test database exists with timeout
        result = subprocess.run([sys.executable, str(script_path), 'info'], 
                              capture_output=True, text=True, timeout=30)
        
        # If info command fails or database doesn't exist, create it
        if result.returncode != 0 or "Does not exist" in result.stdout:
            print("📝 Test database not found, creating...")
            return setup_test_database()
        elif "Tables: Users(0), Assets(0), Fractions(0)" in result.stdout:
            print("📝 Test database exists but has no data, setting up...")
            # Database exists but empty, set up schema and seed
            if setup_test_database_schema():
                return subprocess.run([sys.executable, str(script_path), 'seed'], 
                                    check=True, capture_output=True, text=True, timeout=60).returncode == 0
            return False
        else:
            print("✅ Test database already exists with data")
            return True
            
    except subprocess.TimeoutExpired:
        print("❌ Database check timed out. Please check if PostgreSQL is running.")
        return False
    except Exception as e:
        print(f"❌ Error checking test database: {e}")
        return setup_test_database()


def reset_test_database():
    """Reset test database."""
    script_path = Path(__file__).parent / 'manage_test_db.py'
    
    print("🔄 Resetting test database...")
    try:
        result = subprocess.run([sys.executable, str(script_path), 'reset'], 
                              check=True, capture_output=True, text=True, timeout=60)
        print("✅ Test database reset completed")
        return True
    except subprocess.TimeoutExpired:
        print("❌ Database reset timed out. Please check if PostgreSQL is running.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Test database reset failed: {e}")
        return False