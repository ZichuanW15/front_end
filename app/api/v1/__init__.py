"""
API v1 package
"""

from flask import Blueprint
from app.api.v1.auth import bp as auth_bp
from app.api.v1.assets import bp as assets_bp
from app.api.v1.users import bp as users_bp
from app.api.v1.transactions import bp as transactions_bp

# Create main v1 blueprint
bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register all v1 blueprints
bp.register_blueprint(auth_bp)
bp.register_blueprint(assets_bp)
bp.register_blueprint(users_bp)
bp.register_blueprint(transactions_bp)