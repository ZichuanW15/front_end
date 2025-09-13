"""
Authentication API endpoints
"""

from flask import Blueprint, request, session
from app.models import User
from app import db
from app.api.errors import AuthenticationError, ValidationError, success_response, error_response
from app.api.decorators import require_json, require_fields, handle_exceptions
import hashlib
import secrets

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['POST'])
@require_json
@require_fields('username', 'password')
@handle_exceptions
def login():
    """
    User login endpoint
    POST /api/v1/auth/login
    Body: {"username": "user1", "password": "password123"}
    """
    try:
        data = request.get_json()
        if not data:
            return error_response("Request must contain JSON data", 400)
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return error_response("Username and password are required", 400)
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return error_response("Invalid credentials", 401)
        
        # Verify password (simple string comparison with plain text passwords from CSV)
        if user.password != password:
            return error_response("Invalid credentials", 401)
        
        # Generate a simple session token (in production, use JWT)
        session_token = secrets.token_urlsafe(32)
        
        # Set Flask session for web interface
        session['user_id'] = user.user_id
        session['username'] = user.username
        session['session_token'] = session_token
        session['is_admin'] = user.is_manager
        
        # Return user info with session token
        user_data = user.to_dict()
        user_data['session_token'] = session_token
        
        return success_response(
            data=user_data,
            message="Login successful"
        )
    except Exception as e:
        return error_response(f"Login failed: {str(e)}", 500)


@bp.route('/logout', methods=['POST'])
@handle_exceptions
def logout():
    """
    User logout endpoint
    POST /api/v1/auth/logout
    """
    # Clear Flask session
    session.clear()
    return success_response(message="Logout successful")


@bp.route('/profile', methods=['GET'])
@handle_exceptions
def get_profile():
    """
    Get current user profile
    GET /api/v1/auth/profile
    """
    # In a real application, you would get the user from the session token
    # For now, we'll return a placeholder
    return success_response(
        data={"message": "Profile endpoint - implement session-based auth"},
        message="Profile retrieved"
    )


@bp.route('/users', methods=['GET'])
@handle_exceptions
def get_users():
    """
    Get all users (for testing purposes)
    GET /api/v1/auth/users
    """
    users = User.query.all()
    users_data = [user.to_dict() for user in users]
    
    return success_response(
        data=users_data,
        message="Users retrieved successfully"
    )


@bp.route('/users/<int:user_id>', methods=['GET'])
@handle_exceptions
def get_user(user_id):
    """
    Get specific user by ID
    GET /api/v1/auth/users/<user_id>
    """
    user = User.query.get(user_id)
    
    if not user:
        from app.api.errors import NotFoundError
        raise NotFoundError("User not found")
    
    return success_response(
        data=user.to_dict(),
        message="User retrieved successfully"
    )