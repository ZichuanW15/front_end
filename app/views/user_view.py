"""
User view for formatting user-related responses.
"""

from flask import jsonify


class UserView:
    """View class for user responses."""
    
    def render_user(self, user):
        """
        Render single user response.
        
        Args:
            user: User model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'user': user.to_dict(),
            'status': 'success'
        })
    
    def render_user_created(self, user):
        """
        Render user creation response.
        
        Args:
            user: Created User model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'user': user.to_dict(),
            'message': 'User created successfully',
            'status': 'success'
        }), 201
    
    def render_user_updated(self, user):
        """
        Render user update response.
        
        Args:
            user: Updated User model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'user': user.to_dict(),
            'message': 'User updated successfully',
            'status': 'success'
        })
    
    def render_user_deleted(self):
        """
        Render user deletion response.
        
        Returns:
            Response: JSON response
        """
        return jsonify({
            'message': 'User deleted successfully',
            'status': 'success'
        })
    
    def render_users_list(self, users):
        """
        Render users list response.
        
        Args:
            users: List of User model instances
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'users': [user.to_dict() for user in users],
            'count': len(users),
            'status': 'success'
        })
    
    def render_managers_list(self, managers):
        """
        Render managers list response.
        
        Args:
            managers: List of manager User model instances
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'managers': [manager.to_dict() for manager in managers],
            'count': len(managers),
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
            'error': 'User Error',
            'message': error_message,
            'status_code': status_code
        }), status_code