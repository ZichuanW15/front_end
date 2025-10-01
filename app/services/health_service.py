"""
Health service for system health checks and monitoring.
"""

from datetime import datetime
from sqlalchemy import text
from app.database import db


class HealthService:
    """Service class for health check operations."""
    
    @staticmethod
    def get_basic_health():
        """
        Get basic health status.
        
        Returns:
            dict: Basic health information
        """
        return {
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'API Backbone',
            'version': '1.0.0'
        }
    
    @staticmethod
    def get_database_health():
        """
        Check database connectivity.
        
        Returns:
            tuple: (status_data, http_status_code)
        """
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            db_status = 'connected'
            error = None
            http_status = 200
        except Exception as e:
            db_status = 'disconnected'
            error = str(e)
            http_status = 503
        
        status_data = {
            'status': 'ok' if db_status == 'connected' else 'error',
            'database': db_status,
            'timestamp': datetime.utcnow().isoformat(),
            'error': error
        }
        
        return status_data, http_status
    
    @staticmethod
    def get_detailed_health():
        """
        Get detailed system health information.
        
        Returns:
            tuple: (status_data, http_status_code)
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
        http_status = 200 if overall_status == 'ok' else 503
        
        status_data = {
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
        }
        
        return status_data, http_status