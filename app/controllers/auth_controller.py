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
            
            # Validate required fields - support both 'login' and 'username' fields
            login_field = login_data.get('login') or login_data.get('username')
            password = login_data.get('password')
            
            if not login_field or not password:
                return self.auth_view.render_error("Username/email and password are required", 400)
            
            # Authenticate user (supports both username and email)
            user, session_data = self.auth_service.login_user(
                login_field, 
                password
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
    
    def verify_token(self):
        """
        Verify session token and return user info.
        This is a workaround for browsers that don't send session cookies properly.
        
        Returns:
            Response: JSON response with user data and session info
        """
        try:
            data = request.get_json()
            if not data or 'session_token' not in data:
                return self.auth_view.render_error("Session token required", 400)
            
            session_token = data['session_token']
            
            # Find user by session token
            from flask import session
            if session.get('session_token') == session_token:
                user = self.auth_service.get_current_user()
                if user:
                    return self.auth_view.render_current_user(user)
            
            return self.auth_view.render_error("Invalid session token", 401)
        except Exception as e:
            return self.auth_view.render_error(str(e), 500)