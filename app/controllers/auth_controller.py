"""
Authentication controller for handling authentication-related requests.
"""

from flask import request
from app.services.auth_service import AuthService
from app.views.auth_view import AuthView
from app.decorators import require_json, require_login


class AuthController:
    """Controller for authentication operations."""
    
    def __init__(self):
        self.auth_service = AuthService()
        self.auth_view = AuthView()
    
    @require_json
    def signup(self):
        """
        Handle user registration request.
        
        Returns:
            Response: JSON response with created user data and session info
        """
        try:
            user_data = request.get_json()
            
            # Validate required fields
            required_fields = ['username', 'password', 'email']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    return self.auth_view.render_error(f"Missing required field: {field}", 400)
            
            # Create user and session
            user, session_data = self.auth_service.signup_user(user_data)
            return self.auth_view.render_signup_success(user, session_data)
            
        except ValueError as e:
            return self.auth_view.render_error(str(e), 400)
        except Exception as e:
            return self.auth_view.render_error(str(e), 500)
    
    @require_json
    def login(self):
        """
        Handle user login request.
        
        Returns:
            Response: JSON response with user data and session info
        """
        try:
            login_data = request.get_json()
            
            # Validate required fields
            if 'username' not in login_data or 'password' not in login_data:
                return self.auth_view.render_error("Username and password are required", 400)
            
            # Authenticate user
            user, session_data = self.auth_service.login_user(
                login_data['username'], 
                login_data['password']
            )
            
            if not user:
                return self.auth_view.render_error("Invalid credentials", 401)
            
            return self.auth_view.render_login_success(user, session_data)
            
        except ValueError as e:
            return self.auth_view.render_error(str(e), 400)
        except Exception as e:
            return self.auth_view.render_error(str(e), 500)
    
    @require_login
    def logout(self):
        """
        Handle user logout request.
        
        Returns:
            Response: JSON response with logout confirmation
        """
        try:
            self.auth_service.logout_user()
            return self.auth_view.render_logout_success()
        except Exception as e:
            return self.auth_view.render_error(str(e), 500)
    
    @require_login
    def get_current_user(self):
        """
        Handle get current user request.
        
        Returns:
            Response: JSON response with current user data
        """
        try:
            from flask import session
            user = self.auth_service.get_current_user()
            if not user:
                return self.auth_view.render_error("User not found", 404)
            
            return self.auth_view.render_current_user(user)
        except Exception as e:
            return self.auth_view.render_error(str(e), 500)