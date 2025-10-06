"""
Test routes for API health checks and testing.
"""

from flask import Blueprint, jsonify


bp = Blueprint("test", __name__)

@bp.route("/")
def index():
    """
    Test endpoint to verify API is running.
    
    Returns:
        JSON response with test message
    """
    return jsonify({"message": "Testing API is running 🚀"})
