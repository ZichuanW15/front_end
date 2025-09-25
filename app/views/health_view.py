"""
Health view for formatting health check responses.
"""

from flask import jsonify


class HealthView:
    """View class for health check responses."""
    
    def render_basic_health(self, health_data):
        """
        Render basic health response.
        
        Args:
            health_data: Dictionary containing health information
            
        Returns:
            Response: JSON response
        """
        return jsonify(health_data)
    
    def render_database_health(self, health_data, http_status):
        """
        Render database health response.
        
        Args:
            health_data: Dictionary containing database health information
            http_status: HTTP status code
            
        Returns:
            Response: JSON response with status code
        """
        return jsonify(health_data), http_status
    
    def render_detailed_health(self, health_data, http_status):
        """
        Render detailed health response.
        
        Args:
            health_data: Dictionary containing detailed health information
            http_status: HTTP status code
            
        Returns:
            Response: JSON response with status code
        """
        return jsonify(health_data), http_status
    
    def render_error(self, error_message, status_code):
        """
        Render error response.
        
        Args:
            error_message: Error message
            status_code: HTTP status code
            
        Returns:
            Response: JSON error response
        """
        return jsonify({
            'error': 'Health Check Error',
            'message': error_message,
            'status_code': status_code
        }), status_code