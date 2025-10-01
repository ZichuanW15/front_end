#!/usr/bin/env python3
"""
Setup test database schema using Flask app.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from app import create_app, db


def setup_test_database_schema():
    """Set up test database schema using Flask app."""
    print("📝 Setting up test database schema using Flask app...")
    
    # Create app with testing config
    app = create_app('testing')
    
    with app.app_context():
        try:
            # Create all tables using SQLAlchemy
            db.create_all()
            print("✅ Test database schema setup completed")
            return True
        except Exception as e:
            print(f"❌ Error setting up test database schema: {e}")
            return False


if __name__ == '__main__':
    success = setup_test_database_schema()
    sys.exit(0 if success else 1)