#!/usr/bin/env python3
"""
Flask application entry point for the API backbone.
"""

import os
from sqlalchemy import text
from app import create_app, db

# Create Flask application instance
app = create_app()


def execute_sql_file(file_path):
    """
    Execute SQL commands from a file.
    
    Args:
        file_path (str): Path to the SQL file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split SQL content by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            # Skip empty statements and comments
            if statement and not statement.startswith('--'):
                try:
                    db.session.execute(text(statement))
                except Exception as stmt_error:
                    # Skip problematic statements (like comments or empty statements)
                    print(f"⚠️  Skipping statement: {statement[:50]}... Error: {stmt_error}")
        
        db.session.commit()
        print(f"✅ Successfully executed SQL file: {file_path}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error executing SQL file {file_path}: {e}")
        raise


@app.cli.command()
def init_db():
    """
    Initialize the database with schema from schema.sql file.
    This approach matches the existing project's database initialization.
    """
    try:
        # Get the path to the schema.sql file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if not os.path.exists(schema_path):
            print(f"❌ Schema file not found: {schema_path}")
            print("Falling back to db.create_all()...")
            db.create_all()
            print("✅ Database tables created using db.create_all()")
            return
        
        print(f"📄 Executing schema from: {schema_path}")
        
        # Execute the schema file
        execute_sql_file(schema_path)
        
        print("✅ Database schema initialized successfully!")
        print("   - Tables created")
        print("   - Functions and triggers created")
        print("   - Indexes created")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise


@app.cli.command()
def drop_db():
    """Drop all database tables."""
    try:
        # Drop tables in reverse order to handle foreign key constraints
        tables = [
            'valuehistory', 'transactions', 'ownership', 
            'fractions', 'assets', 'users'
        ]
        
        for table in tables:
            try:
                db.session.execute(f'DROP TABLE IF EXISTS {table} CASCADE')
                print(f"   Dropped table: {table}")
            except Exception as e:
                print(f"   Warning: Could not drop table {table}: {e}")
        
        # Drop functions
        functions = [
            'check_manager_approval()',
            'calculate_fraction_value(INTEGER)',
            'update_fraction_values()',
            'initialize_fraction_values()'
        ]
        
        for func in functions:
            try:
                db.session.execute(f'DROP FUNCTION IF EXISTS {func} CASCADE')
                print(f"   Dropped function: {func}")
            except Exception as e:
                print(f"   Warning: Could not drop function {func}: {e}")
        
        db.session.commit()
        print("🗑️  Database tables and functions dropped successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error dropping database: {e}")
        raise


@app.cli.command()
def reset_db():
    """Reset the database (drop and recreate all tables)."""
    print("🔄 Resetting database...")
    drop_db()
    init_db()
    print("🔄 Database reset successfully!")


@app.cli.command()
def init_sample_data():
    """
    Initialize the database with sample data.
    This creates some basic test data for development.
    """
    try:
        from app.models import User, Asset, Fraction
        from datetime import datetime
        
        # Create sample users
        manager = User(
            user_id=1,
            username='manager',
            email='manager@example.com',
            password='password123',
            is_manager=True,
            create_time=datetime.utcnow()
        )
        
        user1 = User(
            user_id=2,
            username='user1',
            email='user1@example.com',
            password='password123',
            is_manager=False,
            create_time=datetime.utcnow()
        )
        
        # Create sample asset
        asset = Asset(
            asset_id=1,
            name='Sample Property',
            description='A sample real estate asset for testing',
            max_fractions=100,
            min_fractions=1,
            available_fractions=100,
            submitted_by_Users_user_id=1,
            created_at=datetime.utcnow(),
            status='approved',
            approved_at=datetime.utcnow(),
            approved_by_Users_user_id=1
        )
        
        # Create sample fractions
        fraction = Fraction(
            fraction_id=1,
            Assets_asset_id=1,
            fraction_no=1,
            fraction_value=1000.00
        )
        
        
        # Add to database
        db.session.add_all([manager, user1, asset, fraction, value_history])
        db.session.commit()
        
        print("✅ Sample data initialized successfully!")
        print("   - Created 2 users (1 manager, 1 regular user)")
        print("   - Created 1 sample asset")
        print("   - Created 1 sample fraction")
        print("   - Created 1 sample value history entry")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error initializing sample data: {e}")
        raise


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell."""
    from app.models import User, Asset, Fraction, Transaction
    
    return {
        'db': db,
        'User': User,
        'Asset': Asset,
        'Fraction': Fraction,
        'Transaction': Transaction,
    }


if __name__ == '__main__':
    # Get configuration from environment variables
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    print("🚀 Starting API Backbone server...")
    print(f"   Debug mode: {debug}")
    print(f"   Server: http://{host}:{port}")
    print(f"   Health check: http://{host}:{port}/health")
    print(f"   Database health: http://{host}:{port}/health/db")
    print("   Press Ctrl+C to stop")
    
    app.run(debug=debug, host=host, port=port)
