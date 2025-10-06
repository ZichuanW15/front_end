"""
Database configuration and initialization.
This module provides a centralized way to access the database instance
without creating circular imports.
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance
db = SQLAlchemy()