from flask import Blueprint, request, jsonify
from app.models import User
from app import db
import hashlib

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    POST /login
    Body: {"username": "user1", "password": "password123"}
    """
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username']
        password = data['password']
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Simple password check (in production, use proper hashing)
        # For now, we'll just check if the password matches the stored password
        if user.password != password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Return user info (in production, return JWT token)
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@bp.route('/users', methods=['GET'])
def get_users():
    """
    Get all users (for testing purposes)
    GET /users
    """
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500