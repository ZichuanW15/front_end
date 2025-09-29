"""
Authentication view for formatting authentication-related responses.
"""

from flask import jsonify


class AuthView:
    """View class for authentication responses."""
    
    def render_signup_success(self, user, session_data):
        """
        Render successful signup response.
        
        Args:
            user: User model instance
            session_data: Session data dictionary
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'user': user.to_dict(),
            'session': session_data,
            'message': 'User registered successfully',
            'status': 'success'
        }), 201
    
    def render_login_success(self, user, session_data):
        """
        Render successful login response.
        
        Args:
            user: User model instance
            session_data: Session data dictionary
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'user': user.to_dict(),
            'session': session_data,
            'message': 'Login successful',
            'status': 'success'
        })
    
    def render_logout_success(self):
        """
        Render successful logout response.
        
        Returns:
            Response: JSON response
        """
        return jsonify({
            'message': 'Logout successful',
            'status': 'success'
        })
    
    def render_current_user(self, user):
        """
        Render current user response.
        
        Args:
            user: User model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'user': user.to_dict(),
            'status': 'success'
        })
    
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
            'error': 'Authentication Error',
            'message': error_message,
            'status_code': status_code
        }), status_code