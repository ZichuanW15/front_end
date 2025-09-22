"""
User service for user-related business logic.
"""

from app import db
from app.models import User
from datetime import datetime
from typing import Optional, List, Dict, Any


class UserService:
    """Service class for user operations."""
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> User:
        """
        Create a new user.
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['user_name', 'email', 'password']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        user = User(
            user_name=user_data['user_name'],
            email=user_data['email'],
            password=user_data['password'],
            is_manager=user_data.get('is_manager', False),
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None if not found
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User or None if not found
        """
        return User.query.filter_by(user_name=username).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None if not found
        """
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_users(page: int = 1, per_page: int = 20) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            List of User objects
        """
        return User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        ).items
    
    @staticmethod
    def update_user(user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id: User ID
            user_data: Dictionary containing updated user information
            
        Returns:
            Updated User or None if not found
            
        Raises:
            ValueError: If uniqueness constraints are violated
        """
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Check uniqueness for username if being updated
        if 'user_name' in user_data and user_data['user_name'] != user.user_name:
            existing_user = UserService.get_user_by_username(user_data['user_name'])
            if existing_user and existing_user.user_id != user_id:
                raise ValueError("Username already exists")
        
        # Check uniqueness for email if being updated
        if 'email' in user_data and user_data['email'] != user.email:
            existing_email = UserService.get_user_by_email(user_data['email'])
            if existing_email and existing_email.user_id != user_id:
                raise ValueError("Email already exists")
        
        # Update allowed fields
        allowed_fields = ['user_name', 'email', 'is_manager', 'password']
        for field in allowed_fields:
            if field in user_data:
                setattr(user, field, user_data[field])
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        user = User.query.get(user_id)
        if not user:
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True
    
    @staticmethod
    def get_managers() -> List[User]:
        """
        Get all manager users.
        
        Returns:
            List of manager User objects
        """
        return User.query.filter_by(is_manager=True).all()