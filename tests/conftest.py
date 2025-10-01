"""
Pytest configuration and fixtures for the Provision-it test suite.
Provides test database setup, teardown, and common fixtures.
"""

import os
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app import create_app, db
from app.models import User, Asset, Fraction, Transaction, Offer, AssetValueHistory
from datetime import datetime


@pytest.fixture(scope='session')
def test_database_url():
    """Get test database URL from environment or create from main database URL."""
    test_db_url = os.environ.get('TEST_DATABASE_URL')
    
    if not test_db_url:
        # Create test database URL from main database URL
        main_db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/api_backbone')
        if '/api_backbone' in main_db_url:
            test_db_url = main_db_url.replace('/api_backbone', '/api_backbone_test')
        else:
            test_db_url = 'postgresql://localhost/api_backbone_test'
    
    return test_db_url


@pytest.fixture(scope='session')
def ensure_test_database(test_database_url):
    """Ensure test database exists and is properly set up."""
    # Parse database URL
    import re
    pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, test_database_url)
    
    if not match:
        raise ValueError(f"Invalid test database URL format: {test_database_url}")
    
    user, password, host, port, database = match.groups()
    
    # Connect to PostgreSQL server to create database if needed
    server_conn_params = {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password,
        'database': 'postgres'
    }
    
    try:
        conn = psycopg2.connect(**server_conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        exists = cursor.fetchone() is not None
        
        if not exists:
            print(f"Creating test database: {database}")
            cursor.execute(f'CREATE DATABASE "{database}"')
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        pytest.skip(f"Could not create test database: {e}")
    
    yield test_database_url


@pytest.fixture(scope='function')
def app(ensure_test_database):
    """Create application for testing with test database."""
    # Set test database URL for this test
    os.environ['TEST_DATABASE_URL'] = ensure_test_database
    
    app = create_app('testing')
    
    with app.app_context():
        # Create all tables (but don't drop them to preserve seeded data)
        db.create_all()
        
        yield app
        
        # Don't drop all tables to preserve seeded test data
        # db.drop_all()  # Commented out to preserve seeded data


@pytest.fixture(scope='function')
def client(app):
    """Create test client with session support."""
    return app.test_client(use_cookies=True)


@pytest.fixture(scope='function', autouse=True)
def clean_database(app, request):
    """Clear and re-seed database before each test."""
    # Skip clean database for integration tests
    if 'integration' in str(request.fspath):
        yield
        return
    
    with app.app_context():
        # Ensure all tables exist first
        db.create_all()
        
        # Clear all data
        try:
            db.session.execute(text('TRUNCATE TABLE "AssetValueHistory" CASCADE'))
            db.session.execute(text('TRUNCATE TABLE "Transactions" CASCADE'))
            db.session.execute(text('TRUNCATE TABLE "Offers" CASCADE'))
            db.session.execute(text('TRUNCATE TABLE "Fractions" CASCADE'))
            db.session.execute(text('TRUNCATE TABLE "Assets" CASCADE'))
            db.session.execute(text('TRUNCATE TABLE "Users" CASCADE'))
            db.session.commit()
        except Exception as e:
            # If TRUNCATE fails, try DROP and recreate
            print(f"TRUNCATE failed, recreating tables: {e}")
            db.drop_all()
            db.create_all()
        
        # Re-seed with initial data
        from datetime import datetime
        
        # Create seeded users
        users_data = [
            ('admin', 'admin@test.com', 'admin123', True),
            ('testuser1', 'user1@test.com', 'password123', False),
            ('testuser2', 'user2@test.com', 'password123', False),
            ('manager1', 'manager@test.com', 'manager123', True)
        ]
        
        user_ids = []
        for username, email, password, is_manager in users_data:
            user = User(
                user_name=username,
                email=email,
                password=password,
                is_manager=is_manager,
                is_deleted=False,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()  # Get the ID
            user_ids.append(user.user_id)
        
        # Create seeded assets
        assets_data = [
            ('Test Asset 1', 'Description for test asset 1', 1000, 1, 100, 10000.00),
            ('Test Asset 2', 'Description for test asset 2', 500, 1, 50, 5000.00),
            ('Test Asset 3', 'Description for test asset 3', 200, 1, 20, 2000.00)
        ]
        
        asset_ids = []
        for asset_name, description, total_unit, unit_min, unit_max, total_value in assets_data:
            asset = Asset(
                asset_name=asset_name,
                asset_description=description,
                total_unit=total_unit,
                unit_min=unit_min,
                unit_max=unit_max,
                total_value=total_value,
                created_at=datetime.utcnow()
            )
            db.session.add(asset)
            db.session.flush()  # Get the ID
            asset_ids.append(asset.asset_id)
        
        # Create seeded fractions
        fractions_data = [
            (asset_ids[0], user_ids[1], None, 100, True, 10.00),  # testuser1 owns 100 units of Asset 1
            (asset_ids[0], user_ids[2], None, 50, True, 10.00),   # testuser2 owns 50 units of Asset 1
            (asset_ids[1], user_ids[1], None, 25, True, 10.00),  # testuser1 owns 25 units of Asset 2
            (asset_ids[2], user_ids[3], None, 10, True, 10.00)   # manager1 owns 10 units of Asset 3
        ]
        
        for asset_id, owner_id, parent_fraction_id, units, is_active, value_perunit in fractions_data:
            fraction = Fraction(
                asset_id=asset_id,
                owner_id=owner_id,
                parent_fraction_id=parent_fraction_id,
                units=units,
                is_active=is_active,
                value_perunit=value_perunit,
                created_at=datetime.utcnow()
            )
            db.session.add(fraction)
        
        db.session.commit()
        
        yield  # Test runs here
        
        # Cleanup after test (optional, since we clear before each test anyway)


@pytest.fixture(scope='function')
def db_session(app):
    """Provide database session for testing."""
    with app.app_context():
        yield db.session


@pytest.fixture(scope='function')
def sample_users(db_session):
    """Get existing seeded users for testing."""
    # Check if seeded users already exist
    existing_users = db_session.query(User).filter(
        User.user_name.in_(['admin', 'testuser1', 'testuser2', 'manager1'])
    ).all()
    
    if existing_users:
        # Use existing seeded users
        yield existing_users
    else:
        # Create sample users if they don't exist
        users = [
            User(
                user_id=1,
                user_name='admin',
                email='admin@test.com',
                password='admin123',
                is_manager=True,
                is_deleted=False,
                created_at=datetime.utcnow()
            ),
            User(
                user_id=2,
                user_name='testuser1',
                email='user1@test.com',
                password='password123',
                is_manager=False,
                is_deleted=False,
                created_at=datetime.utcnow()
            ),
            User(
                user_id=3,
                user_name='testuser2',
                email='user2@test.com',
                password='password123',
                is_manager=False,
                is_deleted=False,
                created_at=datetime.utcnow()
            ),
            User(
                user_id=4,
                user_name='manager1',
                email='manager@test.com',
                password='manager123',
                is_manager=True,
                is_deleted=False,
                created_at=datetime.utcnow()
            )
        ]
        
        for user in users:
            db_session.add(user)
        
        db_session.commit()
        
        yield users
        
        # Clean up users
        for user in users:
            db_session.delete(user)
        db_session.commit()


@pytest.fixture(scope='function')
def sample_assets(db_session):
    """Get existing seeded assets or create sample assets for testing."""
    # Check if seeded assets already exist
    existing_assets = db_session.query(Asset).filter(
        Asset.asset_name.in_(['Test Asset 1', 'Test Asset 2', 'Test Asset 3'])
    ).all()
    
    if existing_assets:
        # Use existing seeded assets
        yield existing_assets
    else:
        # Create sample assets if they don't exist (without specifying asset_id)
        assets = [
            Asset(
                asset_name='Test Asset 1',
                asset_description='Description for test asset 1',
                total_unit=1000,
                unit_min=1,
                unit_max=100,
                total_value=10000.00,
                created_at=datetime.utcnow()
            ),
            Asset(
                asset_name='Test Asset 2',
                asset_description='Description for test asset 2',
                total_unit=500,
                unit_min=1,
                unit_max=50,
                total_value=5000.00,
                created_at=datetime.utcnow()
            ),
            Asset(
                asset_name='Test Asset 3',
                asset_description='Description for test asset 3',
                total_unit=200,
                unit_min=1,
                unit_max=20,
                total_value=2000.00,
                created_at=datetime.utcnow()
            )
        ]
        
        for asset in assets:
            db_session.add(asset)
        
        db_session.commit()
        
        yield assets
        
        # Clean up assets
        for asset in assets:
            db_session.delete(asset)
        db_session.commit()


@pytest.fixture(scope='function')
def sample_fractions(db_session, sample_users, sample_assets):
    """Get existing seeded fractions or create sample fractions for testing."""
    # Check if seeded fractions already exist
    existing_fractions = db_session.query(Fraction).filter(
        Fraction.units.in_([100, 50, 25, 10])
    ).all()
    
    if existing_fractions:
        # Use existing seeded fractions
        yield existing_fractions
    else:
        # Create sample fractions if they don't exist (using actual IDs from users and assets)
        # Get the first user and asset IDs
        first_user_id = sample_users[0].user_id if sample_users else 1
        first_asset_id = sample_assets[0].asset_id if sample_assets else 1
        
        fractions = [
            Fraction(
                asset_id=first_asset_id,
                owner_id=first_user_id,
                parent_fraction_id=None,
                units=100,
                is_active=True,
                value_perunit=10.00,
                created_at=datetime.utcnow()
            ),
            Fraction(
                asset_id=first_asset_id,
                owner_id=sample_users[1].user_id if len(sample_users) > 1 else first_user_id,
                parent_fraction_id=None,
                units=50,
                is_active=True,
                value_perunit=10.00,
                created_at=datetime.utcnow()
            ),
            Fraction(
                asset_id=sample_assets[1].asset_id if len(sample_assets) > 1 else first_asset_id,
                owner_id=sample_users[2].user_id if len(sample_users) > 2 else first_user_id,
                parent_fraction_id=None,
                units=25,
                is_active=True,
                value_perunit=20.00,
                created_at=datetime.utcnow()
            ),
            Fraction(
                asset_id=sample_assets[2].asset_id if len(sample_assets) > 2 else first_asset_id,
                owner_id=sample_users[3].user_id if len(sample_users) > 3 else first_user_id,
                parent_fraction_id=None,
                units=10,
                is_active=True,
                value_perunit=100.00,
                created_at=datetime.utcnow()
            )
        ]
        
        for fraction in fractions:
            db_session.add(fraction)
        
        db_session.commit()
        
        yield fractions
        
        # Clean up fractions
        for fraction in fractions:
            db_session.delete(fraction)
        db_session.commit()


@pytest.fixture(scope='function')
def authenticated_user(client, sample_users, app):
    """Create and return authenticated user session."""
    user_data = {
        'username': 'testuser1',
        'password': 'password123'
    }
    
    # Login
    response = client.post('/auth/login', 
                         json=user_data,
                         content_type='application/json')
    
    assert response.status_code == 200
    login_data = response.get_json()
    
    # Set up the session manually for the test client
    with client.session_transaction() as sess:
        sess['user_id'] = sample_users[1].user_id
        sess['session_token'] = login_data['session']['session_token']
    
    return {
        'user': sample_users[1],  # testuser1
        'response': login_data,
        'session_token': login_data['session']['session_token']
    }


@pytest.fixture(scope='function')
def authenticated_admin(client, sample_users, app):
    """Create and return authenticated admin user session."""
    user_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # Login
    response = client.post('/auth/login', 
                         json=user_data,
                         content_type='application/json')
    
    assert response.status_code == 200
    login_data = response.get_json()
    
    # Set up the session manually for the test client
    with client.session_transaction() as sess:
        sess['user_id'] = sample_users[0].user_id
        sess['session_token'] = login_data['session']['session_token']
    
    return {
        'user': sample_users[0],  # admin
        'response': login_data,
        'session_token': login_data['session']['session_token']
    }


@pytest.fixture(scope='function')
def sample_offers(db_session, sample_users, sample_assets, sample_fractions):
    """Create sample offers for testing."""
    offers = [
        Offer(
            offer_id=1,
            asset_id=1,
            fraction_id=1,
            user_id=2,
            is_buyer=True,
            units=10,
            price_perunit=12.00,
            create_at=datetime.utcnow()
        ),
        Offer(
            offer_id=2,
            asset_id=2,
            fraction_id=3,
            user_id=4,
            is_buyer=False,
            units=5,
            price_perunit=18.00,
            create_at=datetime.utcnow()
        )
    ]
    
    for offer in offers:
        db_session.add(offer)
    
    db_session.commit()
    
    yield offers
    
    # Clean up offers
    for offer in offers:
        db_session.delete(offer)
    db_session.commit()


@pytest.fixture(scope='function')
def sample_transactions(db_session, sample_users, sample_fractions, sample_offers):
    """Create sample transactions for testing."""
    transactions = [
        Transaction(
            transaction_id=1,
            fraction_id=1,
            unit_moved=10,
            transaction_type='purchase',
            from_owner_id=1,
            to_owner_id=2,
            offer_id=1,
            price_perunit=12.00,
            transaction_at=datetime.utcnow()
        ),
        Transaction(
            transaction_id=2,
            fraction_id=3,
            unit_moved=5,
            transaction_type='sale',
            from_owner_id=3,
            to_owner_id=4,
            offer_id=2,
            price_perunit=18.00,
            transaction_at=datetime.utcnow()
        )
    ]
    
    for transaction in transactions:
        db_session.add(transaction)
    
    db_session.commit()
    
    yield transactions
    
    # Clean up transactions
    for transaction in transactions:
        db_session.delete(transaction)
    db_session.commit()


@pytest.fixture(scope='function')
def sample_asset_value_history(db_session, sample_assets, sample_users):
    """Create sample asset value history for testing."""
    value_history = [
        AssetValueHistory(
            id=1,
            asset_id=1,
            value=10.00,
            source='system',
            adjusted_by=None,
            adjustment_reason='Initial value',
            recorded_at=datetime.utcnow()
        ),
        AssetValueHistory(
            id=2,
            asset_id=1,
            value=12.00,
            source='admin',
            adjusted_by=1,
            adjustment_reason='Value adjustment',
            recorded_at=datetime.utcnow()
        ),
        AssetValueHistory(
            id=3,
            asset_id=2,
            value=20.00,
            source='system',
            adjusted_by=None,
            adjustment_reason='Initial value',
            recorded_at=datetime.utcnow()
        ),
        AssetValueHistory(
            id=4,
            asset_id=3,
            value=100.00,
            source='system',
            adjusted_by=None,
            adjustment_reason='Initial value',
            recorded_at=datetime.utcnow()
        )
    ]
    
    for record in value_history:
        db_session.add(record)
    
    db_session.commit()
    
    yield value_history
    
    # Clean up value history
    for record in value_history:
        db_session.delete(record)
    db_session.commit()


# Markers for different test types
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "database: Tests that require database")
    config.addinivalue_line("markers", "auth: Authentication related tests")
    config.addinivalue_line("markers", "api: API endpoint tests")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if 'unit' in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif 'integration' in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add database marker for tests that use database fixtures
        if any(fixture in item.fixturenames for fixture in ['app', 'db_session', 'client']):
            item.add_marker(pytest.mark.database)
        
        # Add auth marker for authentication tests
        if 'auth' in str(item.fspath) or any('auth' in fixture for fixture in item.fixturenames):
            item.add_marker(pytest.mark.auth)
        
        # Add API marker for API tests
        if any(fixture in item.fixturenames for fixture in ['client', 'authenticated_user', 'authenticated_admin']):
            item.add_marker(pytest.mark.api)