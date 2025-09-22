"""
Flask application factory for the API backbone.
Automatically discovers and registers Blueprints from the routes folder.
"""

import os
import importlib
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import config

# Initialize extensions
db = SQLAlchemy()

# Import models to register them with SQLAlchemy
from . import models

# Import services and controllers to ensure they're available
from . import services
from . import controllers
from . import views


def create_app(config_name=None):
    """
    Application factory pattern.
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
                          If None, uses 'default' configuration.
    
    Returns:
        Flask: Configured Flask application instance
    """
<<<<<<< HEAD
    app = Flask(__name__)
=======
    app = Flask(__name__, static_folder='../frontend', static_url_path='/frontend')
>>>>>>> newrepo/frontend
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Auto-discover and register Blueprints from routes folder
    register_blueprints(app)
    
    # Register shell context for Flask CLI
    register_shell_context(app)
    
    return app


def register_blueprints(app):
    """
    Automatically discover and register Blueprints from app/routes/ folder.
    
    This function scans the routes directory for Python files and imports
    any Blueprint objects named 'bp'. This allows developers to add new
    API endpoints by simply creating a new .py file in the routes folder
    with a Blueprint named 'bp'.
    
    Example routes/health.py:
        from flask import Blueprint
        bp = Blueprint('health', __name__)
        
        @bp.route('/health')
        def health():
            return {'status': 'ok'}
    """
    routes_dir = os.path.join(os.path.dirname(__file__), 'routes')
    
    if not os.path.exists(routes_dir):
        return
    
    # Get all Python files in routes directory
    for filename in os.listdir(routes_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]  # Remove .py extension
            
            try:
                # Import the module
                module = importlib.import_module(f'app.routes.{module_name}')
                
                # Look for a Blueprint named 'bp' in the module
                if hasattr(module, 'bp'):
                    blueprint = getattr(module, 'bp')
                    app.register_blueprint(blueprint)
                    print(f"Registered Blueprint: {blueprint.name}")
                    
            except ImportError as e:
                print(f"Warning: Could not import {module_name}: {e}")
            except Exception as e:
                print(f"Warning: Error registering Blueprint from {module_name}: {e}")


def register_error_handlers(app):
    """Register global error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid.',
            'status_code': 400
        }), 400


def register_shell_context(app):
    """Register shell context for Flask CLI."""
    
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'app': app
        }