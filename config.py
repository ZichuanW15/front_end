"""
Configuration management for the Flask API backbone.
Loads environment variables from .env file and provides configuration classes.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/api_backbone'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API settings
    API_TITLE = 'API Backbone'
    API_VERSION = '1.0.0'
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    
    # Use separate test database to avoid interfering with production data
    TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL')
    if TEST_DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL
    else:
        # Fallback: create test database URL from main database URL
        main_db_url = os.environ.get('DATABASE_URL') or 'postgresql://localhost/api_backbone'
        # Replace database name with test version
        if '/api_backbone' in main_db_url:
            SQLALCHEMY_DATABASE_URI = main_db_url.replace('/api_backbone', '/api_backbone_test')
        else:
            # Extract database name and add _test suffix
            if '/' in main_db_url:
                base_url = main_db_url.rsplit('/', 1)[0]
                db_name = main_db_url.split('/')[-1]
                SQLALCHEMY_DATABASE_URI = f"{base_url}/{db_name}_test"
            else:
                SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/api_backbone_test'
    
    # Test-specific settings
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    PRESERVE_CONTEXT_ON_EXCEPTION = False  # Allow exceptions to propagate


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}