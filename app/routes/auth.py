"""
Authentication routes Blueprint for user authentication.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.auth_controller import AuthController

# Create Blueprint instance
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize controller
auth_controller = AuthController()


@bp.route('/signup', methods=['POST'])
def signup():
    """
    User registration endpoint.
    
    Returns:
        JSON response with created user data and session info
    """
    return auth_controller.signup()


@bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Returns:
        JSON response with user data and session info
    """
    return auth_controller.login()


@bp.route('/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.
    
    Returns:
        JSON response with logout confirmation
    """
    return auth_controller.logout()


@bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current logged-in user information.
    
    Returns:
        JSON response with current user data
    """
    return auth_controller.get_current_user()


@bp.route('/verify', methods=['POST'])
def verify_token():
    """
    Verify session token and return user information.
    Workaround for browsers that don't send session cookies properly.
    
    Returns:
        JSON response with user data
    """
    return auth_controller.verify_token()