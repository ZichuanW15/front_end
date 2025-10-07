"""
Test suite for user authentication and management API endpoints.
"""

import json
import pytest
from flask import session
from app import create_app, db
from app.models import User


class TestUserAuthentication:
    """Test class for user authentication endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create test application."""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def test_user_data(self):
        """Sample user data for testing."""
        return {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'is_manager': False
        }
    
    @pytest.fixture
    def admin_user_data(self):
        """Sample admin user data for testing."""
        return {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'adminpassword123',
            'is_manager': True
        }
    
    def test_signup_success(self, client, test_user_data):
        """Test successful user signup."""
        response = client.post('/api/auth/signup', 
                             data=json.dumps(test_user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert data['message'] == 'User registered successfully'
        assert 'user' in data
        assert 'session' in data
        assert data['user']['user_name'] == test_user_data['username']
        assert data['user']['email'] == test_user_data['email']
        assert data['user']['is_manager'] == test_user_data['is_manager']
        assert 'user_id' in data['user']
        
        # Check session data
        assert 'user_id' in data['session']
        assert 'username' in data['session']
        assert 'session_token' in data['session']
        assert 'is_admin' in data['session']
    
    def test_signup_duplicate_username(self, client, test_user_data):
        """Test signup with duplicate username."""
        # Create first user
        client.post('/api/auth/signup', 
                   data=json.dumps(test_user_data),
                   content_type='application/json')
        
        # Try to create user with same username
        duplicate_data = test_user_data.copy()
        duplicate_data['email'] = 'different@example.com'
        
        response = client.post('/api/auth/signup', 
                             data=json.dumps(duplicate_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Username already exists'
    
    def test_signup_duplicate_email(self, client, test_user_data):
        """Test signup with duplicate email."""
        # Create first user
        client.post('/api/auth/signup', 
                   data=json.dumps(test_user_data),
                   content_type='application/json')
        
        # Try to create user with same email
        duplicate_data = test_user_data.copy()
        duplicate_data['username'] = 'differentuser'
        
        response = client.post('/api/auth/signup', 
                             data=json.dumps(duplicate_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Email already exists'
    
    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields."""
        incomplete_data = {'username': 'testuser'}
        
        response = client.post('/api/auth/signup', 
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required field' in data['message']
    
    def test_signup_no_json(self, client):
        """Test signup without JSON data."""
        response = client.post('/api/auth/signup')
        assert response.status_code == 400
    
    def test_signup_password_mismatch(self, client):
        """Test signup with password confirmation mismatch."""
        signup_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'different123'
        }
        
        response = client.post('/api/auth/signup', 
                             data=json.dumps(signup_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Passwords do not match'
    
    def test_login_success(self, client, test_user_data):
        """Test successful user login."""
        # First create user
        client.post('/api/auth/signup', 
                   data=json.dumps(test_user_data),
                   content_type='application/json')
        
        # Then login
        login_data = {
            'username': test_user_data['username'],
            'password': test_user_data['password']
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert 'session' in data
        assert data['user']['user_name'] == test_user_data['username']
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Invalid credentials'
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        login_data = {'username': 'testuser'}
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Username and password are required'
    
    def test_logout_success(self, client, test_user_data):
        """Test successful logout."""
        # Create and login user
        client.post('/api/auth/signup', 
                   data=json.dumps(test_user_data),
                   content_type='application/json')
        
        login_data = {
            'username': test_user_data['username'],
            'password': test_user_data['password']
        }
        client.post('/api/auth/login', 
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # Logout
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Logout successful'
    
    def test_logout_without_login(self, client):
        """Test logout without being logged in."""
        response = client.post('/api/auth/logout')
        assert response.status_code == 401
    
    def test_get_current_user_success(self, client, test_user_data):
        """Test getting current user information."""
        # Create and login user
        client.post('/api/auth/signup', 
                   data=json.dumps(test_user_data),
                   content_type='application/json')
        
        login_data = {
            'username': test_user_data['username'],
            'password': test_user_data['password']
        }
        client.post('/api/auth/login', 
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # Get current user
        response = client.get('/api/auth/me')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['user_name'] == test_user_data['username']
    
    def test_get_current_user_without_login(self, client):
        """Test getting current user without being logged in."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401


class TestUserManagement:
    """Test class for user management endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create test application."""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create and return authenticated user session."""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'is_manager': False
        }
        
        # Create user
        client.post('/api/auth/signup', 
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Login
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        return json.loads(response.data)
    
    @pytest.fixture
    def authenticated_admin(self, client):
        """Create and return authenticated admin user session."""
        admin_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'adminpassword123',
            'is_manager': True
        }
        
        # Create admin user
        client.post('/api/auth/signup', 
                   data=json.dumps(admin_data),
                   content_type='application/json')
        
        # Login as admin
        login_data = {
            'username': admin_data['username'],
            'password': admin_data['password']
        }
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        return json.loads(response.data)
    
    def test_update_user_profile_success(self, client, authenticated_user):
        """Test successful user profile update."""
        user_id = authenticated_user['user']['user_id']
        
        update_data = {
            'user_name': 'updatedusername',
            'email': 'updated@example.com'
        }
        
        response = client.put(f'/api/users/{user_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['user_name'] == update_data['user_name']
        assert data['user']['email'] == update_data['email']
    
    def test_update_user_profile_unauthorized(self, client, authenticated_user):
        """Test updating another user's profile without authorization."""
        # Create another user
        other_user_data = {
            'username': 'otheruser',
            'email': 'other@example.com',
            'password': 'otherpassword123',
            'is_manager': False
        }
        client.post('/api/auth/signup', 
                   data=json.dumps(other_user_data),
                   content_type='application/json')
        
        # Try to update other user's profile
        update_data = {'user_name': 'hackedusername'}
        
        response = client.put('/api/users/2',  # Assuming other user gets ID 2
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 403
    
    def test_update_user_profile_admin_override(self, client, authenticated_admin):
        """Test admin updating another user's profile."""
        # Create regular user
        user_data = {
            'username': 'regularuser',
            'email': 'regular@example.com',
            'password': 'regularpassword123',
            'is_manager': False
        }
        client.post('/api/auth/signup', 
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Admin updates user profile
        update_data = {'user_name': 'adminupdatedusername'}
        
        response = client.put('/api/users/2',  # Assuming regular user gets ID 2
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['user_name'] == update_data['user_name']
    
    def test_update_user_profile_duplicate_username(self, client, authenticated_user):
        """Test updating profile with duplicate username."""
        # Create another user first
        other_user_data = {
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password': 'existingpassword123',
            'is_manager': False
        }
        client.post('/api/auth/signup', 
                   data=json.dumps(other_user_data),
                   content_type='application/json')
        
        # Try to update current user's username to existing one
        user_id = authenticated_user['user']['user_id']
        update_data = {'user_name': 'existinguser'}
        
        response = client.put(f'/api/users/{user_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Username already exists'
    
    def test_delete_user_success(self, client, authenticated_user):
        """Test successful user deletion."""
        user_id = authenticated_user['user']['user_id']
        
        response = client.delete(f'/api/users/{user_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User deleted successfully'
    
    def test_delete_user_unauthorized(self, client, authenticated_user):
        """Test deleting another user without authorization."""
        # Create another user
        other_user_data = {
            'username': 'otheruser',
            'email': 'other@example.com',
            'password': 'otherpassword123',
            'is_manager': False
        }
        client.post('/api/auth/signup', 
                   data=json.dumps(other_user_data),
                   content_type='application/json')
        
        # Try to delete other user
        response = client.delete('/api/users/2')  # Assuming other user gets ID 2
        assert response.status_code == 403
    
    def test_delete_user_admin_override(self, client, authenticated_admin):
        """Test admin deleting another user."""
        # Create regular user
        user_data = {
            'username': 'regularuser',
            'email': 'regular@example.com',
            'password': 'regularpassword123',
            'is_manager': False
        }
        client.post('/api/auth/signup', 
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Admin deletes user
        response = client.delete('/api/users/2')  # Assuming regular user gets ID 2
        assert response.status_code == 200
    
    def test_delete_nonexistent_user(self, client, authenticated_user):
        """Test deleting a user that doesn't exist."""
        response = client.delete('/api/users/99999')
        assert response.status_code == 404
    
    def test_update_nonexistent_user(self, client, authenticated_user):
        """Test updating a user that doesn't exist."""
        update_data = {'user_name': 'newname'}
        
        response = client.put('/api/users/99999',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 404
    
    def test_unauthorized_access_without_login(self, client):
        """Test accessing protected endpoints without login."""
        # Test update
        response = client.put('/api/users/1',
                            data=json.dumps({'user_name': 'newname'}),
                            content_type='application/json')
        assert response.status_code == 401
        
        # Test delete
        response = client.delete('/api/users/1')
        assert response.status_code == 401