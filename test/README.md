# Test Package

This directory contains all test-related files and utilities for the Provision-it project.

## Structure

```
test/
├── __init__.py              # Package initialization
├── README.md               # This file
├── test_utils/             # Test utilities and helper functions
│   ├── __init__.py
│   └── database_utils.py   # Database test utilities
├── tests/                  # Actual test files
│   ├── __init__.py
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── test_db.py          # Database tests
│   └── test_database_setup.py # Database setup tests
└── test_database/          # Database test management
    ├── manage_test_db.py   # Database setup/teardown script
    └── init_test_db.py     # Database initialization script
```

## Running Tests

From the project root:

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --unit
python run_tests.py --database
python run_tests.py --integration

# With coverage
python run_tests.py --unit --coverage

# Database management
python test/test_database/manage_test_db.py info
python test/test_database/manage_test_db.py reset
python test/test_database/manage_test_db.py full-setup
```

## Test Types

### Unit Tests (`test/tests/unit/`)
- Test individual components in isolation
- Use mocks and fixtures
- Fast execution
- High coverage

### Integration Tests (`test/tests/integration/`)
- Test component interactions
- Use real database connections
- Test API endpoints
- End-to-end workflows

### Database Tests (`test/tests/test_db.py`, `test/tests/test_database_setup.py`)
- Test database schema and setup
- Verify database constraints
- Test data fixtures
- Database isolation

## Test Utilities (`test/test_utils/`)

### `database_utils.py`
- Database creation and setup utilities
- Schema management
- Test data seeding
- Database verification functions

## Database Management (`test/test_database/`)

### `manage_test_db.py`
Main script for managing the test database:
- `create` - Create test database
- `drop` - Drop test database
- `reset` - Reset test database (drop + create)
- `full-setup` - Complete setup (schema + sample data)
- `info` - Show database information

### `init_test_db.py`
Database initialization script used by the main management script.

## Configuration

Tests use pytest with the following configuration:
- `pytest.ini` - Main pytest configuration
- `test/tests/conftest.py` - Test fixtures and configuration
- Environment variables from `.env` file

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Tests should clean up after themselves
3. **Fixtures**: Use pytest fixtures for common setup
4. **Mocking**: Mock external dependencies in unit tests
5. **Coverage**: Aim for high test coverage
6. **Naming**: Use descriptive test names
7. **Documentation**: Document complex test scenarios