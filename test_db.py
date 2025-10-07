#!/usr/bin/env python3
"""
Test script to check database status and registration functionality.
"""

from app import create_app, db
from app.models import User
from datetime import datetime

def test_database():
    app = create_app()
    with app.app_context():
        try:
            # Check if we can query users
            users = User.query.all()
            print(f"✅ Database connection successful!")
            print(f"📊 Total users in database: {len(users)}")
            
            for user in users:
                print(f"   - ID: {user.user_id}, Name: {user.user_name}, Email: {user.email}")
            
            # Test creating a new user
            print("\n🧪 Testing user creation...")
            test_user = User(
                user_name='test_script_user',
                email='test_script@example.com',
                password='test123',
                created_at=datetime.utcnow(),
                is_manager=False
            )
            
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ User created successfully with ID: {test_user.user_id}")
            
            # Verify the user was created
            created_user = User.query.filter_by(user_name='test_script_user').first()
            if created_user:
                print(f"✅ User verification successful: {created_user.user_name}")
            else:
                print("❌ User verification failed")
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_database()

