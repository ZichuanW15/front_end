#!/usr/bin/env python3
"""
Demo script to test the authentication and user management endpoints.
Run this script to verify that all endpoints are working correctly.
"""

import requests
import json
import sys

# Base URL for the API
BASE_URL = 'http://localhost:5000'

def make_request(method, endpoint, data=None, session=None):
    """Make HTTP request with error handling."""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if session:
        # In a real application, you'd handle cookies properly
        # For this demo, we'll just make the requests
        pass
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, data=json.dumps(data), headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, data=json.dumps(data), headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {BASE_URL}")
        print("Make sure the Flask server is running with: python run.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error making request: {e}")
        sys.exit(1)

def test_auth_endpoints():
    """Test all authentication endpoints."""
    print("🔐 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test data
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123',
        'is_manager': False
    }
    
    admin_data = {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'adminpassword123',
        'is_manager': True
    }
    
    # 1. Test Signup
    print("\n1. Testing User Signup...")
    response = make_request('POST', '/api/auth/signup', user_data)
    if response.status_code == 201:
        print("✅ Signup successful")
        user_info = response.json()
        user_id = user_info['user']['user_id']
        print(f"   User ID: {user_id}")
        print(f"   Username: {user_info['user']['user_name']}")
        print(f"   Email: {user_info['user']['email']}")
    else:
        print(f"❌ Signup failed: {response.status_code} - {response.text}")
        return
    
    # 2. Test Admin Signup
    print("\n2. Testing Admin Signup...")
    response = make_request('POST', '/api/auth/signup', admin_data)
    if response.status_code == 201:
        print("✅ Admin signup successful")
        admin_info = response.json()
        admin_id = admin_info['user']['user_id']
        print(f"   Admin ID: {admin_id}")
    else:
        print(f"❌ Admin signup failed: {response.status_code} - {response.text}")
    
    # 3. Test Login
    print("\n3. Testing User Login...")
    login_data = {
        'username': user_data['username'],
        'password': user_data['password']
    }
    response = make_request('POST', '/api/auth/login', login_data)
    if response.status_code == 200:
        print("✅ Login successful")
        login_info = response.json()
        print(f"   User: {login_info['user']['user_name']}")
        print(f"   Session token: {login_info['session']['session_token'][:20]}...")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
    
    # 4. Test Get Current User
    print("\n4. Testing Get Current User...")
    response = make_request('GET', '/api/auth/me')
    if response.status_code == 200:
        print("✅ Get current user successful")
        current_user = response.json()
        print(f"   Current user: {current_user['user']['user_name']}")
    else:
        print(f"❌ Get current user failed: {response.status_code} - {response.text}")
    
    # 5. Test Update User Profile
    print("\n5. Testing Update User Profile...")
    update_data = {
        'user_name': 'updateduser',
        'email': 'updated@example.com'
    }
    response = make_request('PUT', f'/api/users/{user_id}', update_data)
    if response.status_code == 200:
        print("✅ Profile update successful")
        updated_user = response.json()
        print(f"   New username: {updated_user['user']['user_name']}")
        print(f"   New email: {updated_user['user']['email']}")
    else:
        print(f"❌ Profile update failed: {response.status_code} - {response.text}")
    
    # 6. Test Error Cases
    print("\n6. Testing Error Cases...")
    
    # Test duplicate username
    duplicate_user = {
        'username': 'testuser',  # Same username
        'email': 'different@example.com',
        'password': 'password123',
        'is_manager': False
    }
    response = make_request('POST', '/api/auth/signup', duplicate_user)
    if response.status_code == 400:
        print("✅ Duplicate username correctly rejected")
    else:
        print(f"❌ Duplicate username not rejected: {response.status_code}")
    
    # Test invalid login
    invalid_login = {
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }
    response = make_request('POST', '/api/auth/login', invalid_login)
    if response.status_code == 401:
        print("✅ Invalid login correctly rejected")
    else:
        print(f"❌ Invalid login not rejected: {response.status_code}")
    
    # 7. Test Logout
    print("\n7. Testing Logout...")
    response = make_request('POST', '/api/auth/logout')
    if response.status_code == 200:
        print("✅ Logout successful")
    else:
        print(f"❌ Logout failed: {response.status_code} - {response.text}")
    
    # 8. Test Access After Logout
    print("\n8. Testing Access After Logout...")
    response = make_request('GET', '/api/auth/me')
    if response.status_code == 401:
        print("✅ Access correctly denied after logout")
    else:
        print(f"❌ Access not denied after logout: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication endpoint testing completed!")
    print("\nNote: This demo script doesn't handle session cookies properly.")
    print("In a real application, you would maintain session state between requests.")

def main():
    """Main function."""
    print("🚀 Flask Authentication API Demo")
    print("This script will test all the authentication endpoints.")
    print("Make sure your Flask server is running on http://localhost:5000")
    
    try:
        test_auth_endpoints()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")

if __name__ == '__main__':
    main()