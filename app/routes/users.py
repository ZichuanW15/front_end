"""
User routes Blueprint for user management.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.user_controller import UserController

# Create Blueprint instance
<<<<<<< HEAD
bp = Blueprint('users', __name__, url_prefix='/users')
=======
bp = Blueprint('users', __name__, url_prefix='/api/users')
>>>>>>> newrepo/frontend

# Initialize controller
user_controller = UserController()


@bp.route('', methods=['POST'])
def create_user():
    """
    Create a new user.
    
    Returns:
        JSON response with created user data
    """
    return user_controller.create_user()


@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with user data
    """
    return user_controller.get_user(user_id)


@bp.route('', methods=['GET'])
def get_users():
    """
    Get all users with pagination.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        
    Returns:
        JSON response with users list
    """
    return user_controller.get_users()


@bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update user information.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with updated user data
    """
    return user_controller.update_user(user_id)


@bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with deletion status
    """
    return user_controller.delete_user(user_id)


@bp.route('/managers', methods=['GET'])
def get_managers():
    """
    Get all manager users.
    
    Returns:
        JSON response with managers list
    """
    return user_controller.get_managers()