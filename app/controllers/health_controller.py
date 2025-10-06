"""
Health controller for handling health check requests.
"""

from flask import request
from app.services.health_service import HealthService
from app.views.health_view import HealthView


class HealthController:
    """Controller for health check operations."""
    
    def __init__(self):
        self.health_service = HealthService()
        self.health_view = HealthView()
    
    def get_basic_health(self):
        """
        Handle basic health check request.
        
        Returns:
            Response: JSON response with basic health status
        """
        try:
            health_data = self.health_service.get_basic_health()
            return self.health_view.render_basic_health(health_data)
        except Exception as e:
            return self.health_view.render_error(str(e), 500)
    
    def get_database_health(self):
        """
        Handle database health check request.
        
        Returns:
            Response: JSON response with database health status
        """
        try:
            health_data, http_status = self.health_service.get_database_health()
            return self.health_view.render_database_health(health_data, http_status)
        except Exception as e:
            return self.health_view.render_error(str(e), 500)
    
    def get_detailed_health(self):
        """
        Handle detailed health check request.
        
        Returns:
            Response: JSON response with detailed health status
        """
        try:
            health_data, http_status = self.health_service.get_detailed_health()
            return self.health_view.render_detailed_health(health_data, http_status)
        except Exception as e:
            return self.health_view.render_error(str(e), 500)