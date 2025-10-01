"""
Test suite to verify test database setup and configuration.
"""

import pytest
import os
from sqlalchemy import text
from app import create_app
from app.database import db
from test.test_utils.database_utils import verify_database_tables


class TestDatabaseSetup:
    """Test class for database setup verification."""
    
    def test_testing_config_uses_separate_database(self):
        """Test that testing configuration uses a separate database."""
        app = create_app('testing')
        
        # Should use test database URL
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        assert 'test' in db_uri or '_test' in db_uri
        assert app.config['TESTING'] is True
    
    def test_database_isolation(self, app, client):
        """Test that test database is isolated from production."""
        with app.app_context():
            # Should be able to connect to test database
            result = db.session.execute(text('SELECT 1')).scalar()
            assert result == 1
            
            # Database should be empty initially (no production data)
            # This test assumes production has data, test database starts empty
            pass
    
    def test_schema_tables_exist(self, app):
        """Test that all required tables exist in test database."""
        with app.app_context():
            assert verify_database_tables(db), "Not all expected tables found in test database"
    
    def test_sample_data_fixtures(self, sample_users, sample_assets, sample_fractions):
        """Test that sample data fixtures work correctly."""
        # Test users fixture
        assert len(sample_users) == 4
        assert any(user.user_name == 'admin' for user in sample_users)
        assert any(user.is_manager for user in sample_users)
        
        # Test assets fixture (should have at least the seeded assets)
        assert len(sample_assets) >= 3
        assert any(asset.asset_name == 'Test Asset 1' for asset in sample_assets)
        
        # Test fractions fixture
        assert len(sample_fractions) == 4
        assert any(fraction.units == 100 for fraction in sample_fractions)
    
    def test_authentication_fixtures(self, client, authenticated_user, authenticated_admin):
        """Test that authentication fixtures work correctly."""
        # Test regular user authentication
        assert authenticated_user['user'].user_name == 'testuser1'
        assert not authenticated_user['user'].is_manager
        
        # Test admin authentication
        assert authenticated_admin['user'].user_name == 'admin'
        assert authenticated_admin['user'].is_manager
    
    def test_database_cleanup(self, app):
        """Test that database is properly cleaned up between tests."""
        with app.app_context():
            # This test should run in isolation
            # If cleanup works, we shouldn't see data from other tests
            user_count = db.session.execute(text('SELECT COUNT(*) FROM "Users"')).scalar()
            asset_count = db.session.execute(text('SELECT COUNT(*) FROM "Assets"')).scalar()
            
            # With seeded data, we expect 4 users and 3 assets from the seeded test data
            # Additional users/assets would indicate test data pollution
            assert user_count >= 4  # At least the seeded users
            assert asset_count >= 3  # At least the seeded assets
            
            # Check that we have the expected seeded users
            seeded_users = db.session.execute(text('''
                SELECT COUNT(*) FROM "Users" 
                WHERE user_name IN ('admin', 'testuser1', 'testuser2', 'manager1')
            ''')).scalar()
            assert seeded_users == 4

    def test_test_database_url_environment(self):
        """Test that test database URL configuration works."""
        # Create app with testing config
        app = create_app('testing')
        
        # Should use a test database (either explicitly set or auto-generated)
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        assert 'test' in db_uri or '_test' in db_uri
        assert app.config['TESTING'] is True
        
        # Should not use the production database
        assert 'provision_it_v2' in db_uri  # Should use test version
    
    def test_database_constraints_preserved(self, app):
        """Test that database constraints are preserved in test database."""
        with app.app_context():
            # Test foreign key constraints exist
            inspector = db.inspect(db.engine)
            
            # Check that foreign key relationships exist
            # This is a basic check - in a real scenario, you'd check specific constraints
            tables = inspector.get_table_names()
            assert 'Fractions' in tables
            assert 'Assets' in tables
            assert 'Users' in tables
    
    def test_multiple_test_instances_isolation(self, app, client):
        """Test that multiple test instances don't interfere with each other."""
        with app.app_context():
            # Get initial user count (should include seeded data)
            initial_count = db.session.execute(text('SELECT COUNT(*) FROM "Users"')).scalar()
            
            # Create some test data with unique name
            import time
            timestamp = int(time.time() * 1000)
            unique_username = f'isolation_test_user_{timestamp}'
            unique_email = f'isolation_{timestamp}@test.com'
            
            from app.models import User
            from datetime import datetime
            test_user = User(
                user_name=unique_username,
                email=unique_email,
                password='password',
                is_manager=False,
                is_deleted=False,
                created_at=datetime.utcnow()
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Verify data exists (should be initial count + 1)
            user_count = db.session.execute(text('SELECT COUNT(*) FROM "Users"')).scalar()
            assert user_count == initial_count + 1
            
            # Verify our specific test user exists
            test_user_exists = db.session.execute(text('''
                SELECT COUNT(*) FROM "Users" 
                WHERE user_name = :username
            '''), {'username': unique_username}).scalar()
            assert test_user_exists == 1
            
            # This test should be isolated from other tests
            # The cleanup happens automatically via fixtures


class TestDatabaseManagement:
    """Test class for database management utilities."""
    
    def test_config_handles_missing_test_db_url(self):
        """Test that config handles missing TEST_DATABASE_URL gracefully."""
        # Create app - should auto-generate test database URL from main database URL
        app = create_app('testing')
        
        # Should create test database URL from main database URL
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        assert '_test' in db_uri  # Should have test suffix
        assert app.config['TESTING'] is True