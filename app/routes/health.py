"""
Health check Blueprint for API monitoring and status verification.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.health_controller import HealthController

# Create Blueprint instance
bp = Blueprint('health', __name__)

# Initialize controller
health_controller = HealthController()


@bp.route('/health')
def health():
    """
    Basic health check endpoint.
    
    Returns:
        JSON response with API status and timestamp
    """
    return health_controller.get_basic_health()


@bp.route('/health/db')
def health_db():
    """
    Database connectivity health check.
    
    Returns:
        JSON response with database connection status
    """
    return health_controller.get_database_health()


@bp.route('/health/detailed')
def health_detailed():
    """
    Detailed health check with system information.
    
    Returns:
        JSON response with comprehensive system status
    """
    return health_controller.get_detailed_health()