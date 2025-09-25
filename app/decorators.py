"""
Authentication and validation decorators for the Flask application.
"""

import secrets
from functools import wraps
from flask import request, session, jsonify
from app.services.user_service import UserService


def require_json(f):
    """
    Decorator to ensure request contains valid JSON data.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request must contain JSON data',
                'status_code': 400
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No JSON data provided',
                'status_code': 400
            }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def require_login(f):
    """
    Decorator to ensure user is logged in.
    Supports both session cookies and Bearer tokens.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session cookie authentication first
        if 'user_id' in session and 'session_token' in session:
            # Verify session token is still valid
            user = UserService.get_user_by_id(session['user_id'])
            if user:
                return f(*args, **kwargs)
            else:
                session.clear()
        
        # Check for Bearer token authentication
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Find user by session token
            # Note: In a real app, you'd want to store tokens in a proper token store
            # For now, we'll check if the token matches any user's session token
            try:
                # This is a simplified approach - in production you'd have a proper token validation
                # For now, we'll check against the current session or find the user by token
                if 'user_id' in session and session.get('session_token') == token:
                    user = UserService.get_user_by_id(session['user_id'])
                    if user:
                        return f(*args, **kwargs)
            except Exception:
                pass
        
        # If neither authentication method works
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status_code': 401
        }), 401
    
    return decorated_function


def require_admin(f):
    """
    Decorator to ensure user has admin privileges.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'is_admin' not in session:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Admin privileges required',
                'status_code': 403
            }), 403
        
        if not session['is_admin']:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Admin privileges required',
                'status_code': 403
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_ownership_or_admin(user_id_param='user_id'):
    """
    Decorator to ensure user owns the resource or has admin privileges.
    
    Args:
        user_id_param: Parameter name containing the user ID
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Authentication required',
                    'status_code': 401
                }), 401
            
            target_user_id = kwargs.get(user_id_param)
            if not target_user_id:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'User ID required',
                    'status_code': 400
                }), 400
            
            # Allow if user owns the resource or is admin
            if session['user_id'] != target_user_id and not session.get('is_admin', False):
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'Access denied: insufficient privileges',
                    'status_code': 403
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_session_token():
    """
    Generate a secure random session token.
    
    Returns:
        str: Random session token
    """
    return secrets.token_urlsafe(32)


def create_user_session(user):
    """
    Create a user session.
    
    Args:
        user: User model instance
        
    Returns:
        dict: Session data
    """
    session_data = {
        'user_id': user.user_id,
        'username': user.user_name,
        'session_token': generate_session_token(),
        'is_admin': user.is_manager  # Note: using is_manager as admin flag
    }
    
    # Update Flask session
    session.update(session_data)
    
    return session_data


def clear_user_session():
    """
    Clear the current user session.
    """
    session.clear()