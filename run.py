#!/usr/bin/env python3
"""
Flask application entry point for the Provision-it fractional ownership API.
"""

import os
from app import create_app, db
from app.models import User, Asset, Fraction, Ownership, Transaction, ValueHistory

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell."""
    return {
        'db': db,
        'User': User,
        'Asset': Asset,
        'Fraction': Fraction,
        'Ownership': Ownership,
        'Transaction': Transaction,
        'ValueHistory': ValueHistory
    }

@app.cli.command()
def init_db():
    """Initialize the database with tables."""
    db.create_all()
    print("Database tables created successfully!")

@app.cli.command()
def drop_db():
    """Drop all database tables."""
    db.drop_all()
    print("Database tables dropped successfully!")

if __name__ == '__main__':
    # Get configuration from environment variables
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    print(f"Starting Provision-it API server...")
    print(f"Debug mode: {debug}")
    print(f"Server: http://{host}:{port}")
    print(f"API endpoints available at: http://{host}:{port}/api/")
    
    app.run(debug=debug, host=host, port=port)