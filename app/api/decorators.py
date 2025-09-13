"""
Decorators for common API functionality
"""

from functools import wraps
from flask import request, jsonify
from app.api.errors import AuthenticationError, ValidationError
from app.models import User


def require_json(f):
    """Decorator to ensure request contains JSON data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            raise ValidationError("Request must contain JSON data")
        return f(*args, **kwargs)
    return decorated_function


def require_fields(*required_fields):
    """Decorator to ensure required fields are present in JSON data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                raise ValidationError("Request must contain JSON data")
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_date_format(date_string):
    """Validate date format (YYYY-MM-DD)"""
    from datetime import datetime
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def paginate(page=1, per_page=20, max_per_page=100):
    """Decorator to add pagination to endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get pagination parameters from query string
            page_num = request.args.get('page', page, type=int)
            per_page_num = request.args.get('per_page', per_page, type=int)
            
            # Validate pagination parameters
            if page_num < 1:
                page_num = 1
            if per_page_num < 1:
                per_page_num = per_page
            if per_page_num > max_per_page:
                per_page_num = max_per_page
            
            # Add pagination info to kwargs
            kwargs['page'] = page_num
            kwargs['per_page'] = per_page_num
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def handle_exceptions(f):
    """Decorator to handle common exceptions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            from app.api.errors import error_response, APIError
            # Re-raise APIError exceptions so they can be handled by the error handlers
            if isinstance(e, APIError):
                raise e
            return error_response(f"An error occurred: {str(e)}", 500)
    return decorated_function