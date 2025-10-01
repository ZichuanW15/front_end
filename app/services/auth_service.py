"""
Authentication service for user authentication business logic.
"""

from flask import session
from app.database import db
from app.models import User
from app.services.user_service import UserService
from app.decorators import create_user_session, clear_user_session
from datetime import datetime
from typing import Optional, Tuple, Dict, Any


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    def signup_user(user_data: Dict[str, Any]) -> Tuple[User, Dict[str, Any]]:
        """
        Create a new user and establish session.
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Tuple of (User, session_data)
            
        Raises:
            ValueError: If user already exists or validation fails
        """
        username = user_data['username']
        email = user_data['email']
        password = user_data['password']
        confirm_password = user_data.get('confirm_password')
        
        # Validate password confirmation
        if confirm_password and password != confirm_password:
            raise ValueError("Passwords do not match")
        
        # Check if username already exists (active users only)
        existing_user = UserService.get_user_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")
        
        # Check if email already exists (active users only)
        existing_email = UserService.get_user_by_email(email)
        if existing_email:
            raise ValueError("Email already exists")
        
        # Check if there's a soft-deleted user with same username or email
        soft_deleted_user = UserService.get_soft_deleted_user_by_username(username)
        soft_deleted_email = UserService.get_soft_deleted_user_by_email(email)
        
        # If both username and email match a soft-deleted user, reactivate it
        if soft_deleted_user and soft_deleted_email and soft_deleted_user.user_id == soft_deleted_email.user_id:
            # Reactivate the soft-deleted user
            user = UserService.reactivate_user(soft_deleted_user)
            # Update user data
            user.user_name = username
            user.email = email
            user.password = password
            user.is_manager = user_data.get('is_manager', False)
            db.session.commit()
        elif soft_deleted_user or soft_deleted_email:
            # If only username or email matches a soft-deleted user, create new user
            # This allows re-registration with same credentials
            create_data = {
                'user_name': username,
                'email': email,
                'password': password,  # Note: In production, hash this password
                'is_manager': user_data.get('is_manager', False)
            }
            user = UserService.create_user(create_data)
        else:
            # Create new user
            create_data = {
                'user_name': username,
                'email': email,
                'password': password,  # Note: In production, hash this password
                'is_manager': user_data.get('is_manager', False)
            }
            user = UserService.create_user(create_data)
        
        # Create session
        session_data = create_user_session(user)
        
        return user, session_data
    
    @staticmethod
    def login_user(login_field: str, password: str) -> Tuple[Optional[User], Optional[Dict[str, Any]]]:
        """
        Authenticate user and establish session.
        Soft-deleted users cannot login.
        
        Args:
            login_field: Username or email
            password: Password (plaintext for now)
            
        Returns:
            Tuple of (User, session_data) or (None, None) if authentication fails
        """
        # Try to get user by username first, then by email
        # get_user_by_username and get_user_by_email already filter out soft-deleted users
        user = UserService.get_user_by_username(login_field)
        if not user:
            user = UserService.get_user_by_email(login_field)
        
        if not user:
            return None, None
        
        # Verify password (plaintext comparison for now)
        if user.password != password:
            return None, None
        
        # Create session
        session_data = create_user_session(user)
        
        return user, session_data
    
    @staticmethod
    def logout_user() -> None:
        """
        Logout current user and clear session.
        """
        clear_user_session()
    
    @staticmethod
    def get_current_user() -> Optional[User]:
        """
        Get current logged-in user.
        
        Returns:
            User or None if not logged in
        """
        if 'user_id' not in session:
            return None
        
        return UserService.get_user_by_id(session['user_id'])
    
    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if user is currently authenticated.
        
        Returns:
            True if user is authenticated, False otherwise
        """
        return 'user_id' in session and 'session_token' in session
    
    @staticmethod
    def is_admin() -> bool:
        """
        Check if current user has admin privileges.
        
        Returns:
            True if user is admin, False otherwise
        """
        return session.get('is_admin', False)