#!/usr/bin/env python3
"""
Comprehensive test runner for the Provision-it project.
Handles unit tests, integration tests, Playwright tests, and Flask app management.
"""

import sys
import subprocess
import argparse
import os
import time
import threading
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print('='*60)


def print_step(step, description):
    """Print a step indicator."""
    print(f"\n📋 Step {step}: {description}")


def run_command(cmd, description, capture_output=False):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=capture_output, text=True)
        print(f"✅ {description} completed successfully")
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        return False, e.stderr if capture_output else ""


def check_environment():
    """Check if required environment is set up."""
    print_step(1, "Checking environment setup")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠️  Warning: .env file not found")
        print("   Make sure you have configured your database settings")
        print("   You can run: python setup_env.sh (Linux/Mac) or setup_env.bat (Windows)")
        return False
    
    # Check if DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("⚠️  Warning: DATABASE_URL not set in environment")
        print("   Please set DATABASE_URL in your .env file")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not activated")
        print("   Please activate your virtual environment first:")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate    # Windows")
        return False
    
    # Check if required packages are installed
    try:
        import psycopg2
        print("✅ PostgreSQL driver (psycopg2) is available")
    except ImportError:
        print("❌ Error: psycopg2 not installed")
        print("   Please install dependencies: pip install -r requirements.txt")
        return False
    
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ Error: pytest not installed")
        print("   Please install dependencies: pip install -r requirements.txt")
        return False
    
    print("✅ Environment check completed")
    return True


def check_flask_app():
    """Check if Flask app is running."""
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Flask application is running on http://localhost:5000")
            return True
    except Exception:
        pass
    return False


def start_flask_app():
    """Start Flask app in background."""
    print("🔄 Starting Flask application...")
    
    # Start Flask app in background
    flask_process = subprocess.Popen(
        [sys.executable, 'run.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for Flask app to start
    for i in range(30):  # Wait up to 30 seconds
        time.sleep(1)
        if check_flask_app():
            print("✅ Flask application started successfully")
            return flask_process
        print(f"   Waiting for Flask app... ({i+1}/30)")
    
    print("❌ Flask application failed to start")
    flask_process.terminate()
    return None


def stop_flask_app(flask_process):
    """Stop Flask app."""
    if flask_process:
        print("🔄 Stopping Flask application...")
        flask_process.terminate()
        flask_process.wait()
        print("✅ Flask application stopped")


def setup_playwright():
    """Set up Playwright if needed."""
    try:
        import playwright
        print("✅ Playwright is available")
        return True
    except ImportError:
        print("🔄 Installing Playwright...")
        success, _ = run_command([
            sys.executable, '-m', 'pip', 'install', 'playwright', 'pytest-playwright'
        ], "Installing Playwright packages")
        
        if not success:
            return False
        
        # Install browser
        success, _ = run_command([
            sys.executable, '-m', 'playwright', 'install', 'chromium'
        ], "Installing Chromium browser")
        
        return success


def setup_test_database():
    """Set up test database with fresh data."""
    print_step(2, "Setting up test database")
    
    try:
        # Always reset the test database to ensure clean state
        script_path = Path('test/test_database/manage_test_db.py')
        if script_path.exists():
            print("🔄 Resetting test database for clean test run...")
            success, _ = run_command(['python', str(script_path), 'reset'], 
                                   "Reset test database", capture_output=True)
            if not success:
                print("❌ Test database reset failed")
                return False
            
            print("📝 Setting up fresh test database...")
            success, _ = run_command(['python', str(script_path), 'full-setup'], 
                                   "Setup test database", capture_output=True)
            if success:
                print("✅ Test database setup completed")
                return True
            else:
                print("❌ Test database setup failed")
                return False
        else:
            print("❌ Test database management script not found")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up test database: {e}")
        return False


def run_tests(args):
    """Run the actual tests."""
    print_step(3, "Running tests")
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    
    # Determine test scope
    if args.unit:
        cmd.extend(['test/tests/unit/', '--maxfail=1'])
        test_type = "Unit Tests"
    elif args.integration:
        cmd.extend(['test/tests/integration/test_playwright_integration.py', '--maxfail=1'])
        test_type = "Integration Tests (Playwright)"
    elif args.playwright:
        cmd.extend(['test/tests/integration/test_playwright_integration.py', '--maxfail=1'])
        test_type = "Playwright Integration Tests"
    elif args.database:
        cmd.extend(['test/tests/test_db.py', 'test/tests/test_database_setup.py', '--maxfail=1'])
        test_type = "Database Tests"
    else:
        cmd.extend(['test/tests/', '--maxfail=1'])
        test_type = "All Tests"
    
    # Add coverage if requested
    if args.coverage and not args.fast:
        cmd.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-report=xml:coverage.xml',
            '--cov-fail-under=40'
        ])
    
    # Add other options
    cmd.extend([
        '--disable-warnings',
        '--tb=short'
    ])
    
    # Run the tests
    success, output = run_command(cmd, f"Running {test_type}")
    
    if success:
        print(f"\n🎉 {test_type} completed successfully!")
        if args.coverage and not args.fast:
            print("\n📊 Coverage report generated:")
            print("   - HTML: htmlcov/index.html")
            print("   - XML:  coverage.xml")
    else:
        print(f"\n💥 {test_type} failed!")
        if output:
            print(f"Output: {output}")
    
    return success


def main():
    parser = argparse.ArgumentParser(description='Run tests for Provision-it project with automatic test database setup')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests (Playwright) only')
    parser.add_argument('--playwright', action='store_true', help='Run Playwright tests only (same as --integration)')
    parser.add_argument('--database', action='store_true', help='Run database tests only')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fast', action='store_true', help='Run tests quickly (no coverage)')
    parser.add_argument('--skip-db-setup', action='store_true', help='Skip test database setup')
    parser.add_argument('--reset-db', action='store_true', help='Reset test database before running tests')
    parser.add_argument('--auto-flask', action='store_true', help='Automatically start/stop Flask app for Playwright tests')
    parser.add_argument('--skip-flask-check', action='store_true', help='Skip Flask app availability check')
    
    args = parser.parse_args()
    
    print_header("Provision-it Comprehensive Test Runner")
    print("This script handles unit tests, integration tests, Playwright tests, and Flask app management.")
    
    # Check environment
    if not check_environment():
        print_header("Environment Setup Required! ⚠️")
        print("\n🔧 Please fix the environment issues above and try again.")
        print("\n💡 Quick setup:")
        print("   1. Activate virtual environment: source venv/bin/activate")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Run tests: python run_tests.py")
        sys.exit(1)
    
    # Setup Playwright if needed for Playwright/integration tests
    if args.playwright or args.integration or (not args.unit and not args.database):
        if not setup_playwright():
            print("❌ Playwright setup failed. Exiting.")
            sys.exit(1)
    
    # Handle Flask app for Playwright/integration tests
    flask_process = None
    if args.playwright or args.integration or (not args.unit and not args.database):
        if not args.skip_flask_check:
            if not check_flask_app():
                if args.auto_flask:
                    flask_process = start_flask_app()
                    if not flask_process:
                        print("❌ Failed to start Flask app. Exiting.")
                        sys.exit(1)
                else:
                    print_header("Flask Application Required! ⚠️")
                    print("\n🔧 Please start your Flask application and try again.")
                    print("\n💡 Options:")
                    print("   1. Start Flask app manually: python run.py")
                    print("   2. Use --auto-flask to start Flask app automatically")
                    print("   3. Use --skip-flask-check to skip this check")
                    sys.exit(1)
    
    try:
        # Setup test database unless skipped
        if not args.skip_db_setup:
            if args.reset_db:
                print_step(2, "Resetting test database")
                try:
                    from test_database.setup import reset_test_database
                    success = reset_test_database()
                    if not success:
                        print("❌ Test database reset failed")
                        sys.exit(1)
                except ImportError:
                    script_path = Path('test/test_database/manage_test_db.py')
                    if script_path.exists():
                        success, _ = run_command(['python', str(script_path), 'reset'], 
                                               "Manual test database reset", capture_output=True)
                        if not success:
                            sys.exit(1)
            
            success = setup_test_database()
            if not success:
                print("❌ Test database setup failed. Exiting.")
                sys.exit(1)
        else:
            print_step(2, "Skipping test database setup (--skip-db-setup)")
        
        # Run tests
        success = run_tests(args)
        
        if success:
            print_header("Test Run Completed Successfully! 🎉")
            print("\n💡 Tips:")
            print("   - Use --coverage to see test coverage")
            print("   - Use --verbose for detailed output")
            print("   - Use --reset-db to reset test database")
            print("   - Use --auto-flask for Playwright tests")
            print("   - Use --skip-db-setup to skip database setup")
        else:
            print_header("Test Run Failed! 💥")
            print("\n🔧 Troubleshooting:")
            print("   - Check test database setup: python test/test_database/manage_test_db.py info")
            print("   - Reset test database: python test/test_database/manage_test_db.py reset")
            print("   - Run tests with --verbose for more details")
            sys.exit(1)
    
    finally:
        # Clean up Flask app if we started it
        if flask_process:
            stop_flask_app(flask_process)


if __name__ == '__main__':
    main()