"""
Health check Blueprint for API monitoring and status verification.
"""

from flask import Blueprint, jsonify
from sqlalchemy import text
from app import db
from datetime import datetime

# Create Blueprint instance
bp = Blueprint('health', __name__)


@bp.route('/health')
def health():
    """
    Basic health check endpoint.
    
    Returns:
        JSON response with API status and timestamp
    """
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'API Backbone',
        'version': '1.0.0'
    })


@bp.route('/health/db')
def health_db():
    """
    Database connectivity health check.
    
    Returns:
        JSON response with database connection status
    """
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
        error = None
    except Exception as e:
        db_status = 'disconnected'
        error = str(e)
    
    return jsonify({
        'status': 'ok' if db_status == 'connected' else 'error',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat(),
        'error': error
    }), 200 if db_status == 'connected' else 503


@bp.route('/health/detailed')
def health_detailed():
    """
    Detailed health check with system information.
    
    Returns:
        JSON response with comprehensive system status
    """
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
        db_error = None
    except Exception as e:
        db_status = 'disconnected'
        db_error = str(e)
    
    # Overall status
    overall_status = 'ok' if db_status == 'connected' else 'degraded'
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'API Backbone',
        'version': '1.0.0',
        'components': {
            'database': {
                'status': db_status,
                'error': db_error
            }
        }
    }), 200 if overall_status == 'ok' else 503