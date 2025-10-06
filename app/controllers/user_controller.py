"""
User controller for handling user-related requests.
"""

from flask import request
from app.services.user_service import UserService
from app.views.user_view import UserView
from app.decorators import require_json, require_login, require_ownership_or_admin


class UserController:
    """Controller for user operations."""
    
    def __init__(self):
        self.user_service = UserService()
        self.user_view = UserView()
    
    @require_json
    def create_user(self):
        """
        Handle user creation request.
        
        Returns:
            Response: JSON response with created user data
        """
        try:
            user_data = request.get_json()
            
            user = self.user_service.create_user(user_data)
            return self.user_view.render_user_created(user)
        except ValueError as e:
            return self.user_view.render_error(str(e), 400)
        except Exception as e:
            return self.user_view.render_error(str(e), 500)
    
    def get_user(self, user_id):
        """
        Handle get user by ID request.
        
        Args:
            user_id: User ID
            
        Returns:
            Response: JSON response with user data
        """
        try:
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return self.user_view.render_error("User not found", 404)
            
            return self.user_view.render_user(user)
        except Exception as e:
            return self.user_view.render_error(str(e), 500)
    
    def get_users(self):
        """
        Handle get all users request.
        
        Returns:
            Response: JSON response with users list
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            users = self.user_service.get_all_users(page, per_page)
            return self.user_view.render_users_list(users)
        except Exception as e:
            return self.user_view.render_error(str(e), 500)
    
    @require_json
    def update_user(self, user_id):
        """
        Handle user update request.
        Uses password verification for authentication (simpler approach).
        
        Args:
            user_id: User ID
            
        Returns:
            Response: JSON response with updated user data
        """
        try:
            user_data = request.get_json()
            
            # Get current password for verification
            current_password = user_data.pop('current_password', None)
            if not current_password:
                return self.user_view.render_error("Current password required for verification", 401)
            
            # Get the user to verify password
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return self.user_view.render_error("User not found", 404)
            
            # Verify current password
            if user.password != current_password:
                return self.user_view.render_error("Invalid current password", 401)
            
            # Update user
            updated_user = self.user_service.update_user(user_id, user_data)
            if not updated_user:
                return self.user_view.render_error("Failed to update user", 500)
            
            return self.user_view.render_user_updated(updated_user)
        except ValueError as e:
            return self.user_view.render_error(str(e), 400)
        except Exception as e:
            return self.user_view.render_error(str(e), 500)
    
    def delete_user(self, user_id):
        """
        Handle user deletion request.
        Uses password verification for authentication.
        
        Args:
            user_id: User ID
            
        Returns:
            Response: JSON response with deletion status
        """
        try:
            user_data = request.get_json() or {}
            
            # Get current password for verification
            current_password = user_data.get('current_password')
            if not current_password:
                return self.user_view.render_error("Current password required for account deletion", 401)
            
            # Get the user to verify password
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return self.user_view.render_error("User not found", 404)
            
            # Verify current password
            if user.password != current_password:
                return self.user_view.render_error("Invalid current password", 401)
            
            # Attempt to delete user with ownership checks
            result = self.user_service.delete_user(user_id)
            
            if result["success"]:
                return self.user_view.render_user_deleted()
            else:
                return self.user_view.render_error(result["message"], 400)
                
        except Exception as e:
            return self.user_view.render_error(str(e), 500)
    
    def get_managers(self):
        """
        Handle get managers request.
        
        Returns:
            Response: JSON response with managers list
        """
        try:
            managers = self.user_service.get_managers()
            return self.user_view.render_managers_list(managers)
        except Exception as e:
            return self.user_view.render_error(str(e), 500)