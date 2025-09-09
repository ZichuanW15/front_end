"""
Error handling and response formatting for the API
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """Base API exception class"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(APIError):
    """Validation error exception"""
    def __init__(self, message, field=None):
        super().__init__(message, 400)
        self.field = field


class NotFoundError(APIError):
    """Resource not found exception"""
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)


class AuthenticationError(APIError):
    """Authentication error exception"""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, 401)


class AuthorizationError(APIError):
    """Authorization error exception"""
    def __init__(self, message="Access denied"):
        super().__init__(message, 403)


def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = jsonify({
            'error': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500
        }), 500


def success_response(data=None, message="Success", status_code=200):
    """Create a standardized success response"""
    response = {
        'status': 'success',
        'message': message,
        'status_code': status_code
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error_response(message, status_code=400, errors=None):
    """Create a standardized error response"""
    response = {
        'status': 'error',
        'message': message,
        'status_code': status_code
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code