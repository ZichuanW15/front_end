@echo off
REM Setup script for Provision-it Flask API (Windows)
REM This script creates a virtual environment and installs dependencies

echo 🚀 Setting up Provision-it Flask API environment...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python version:
python --version

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
echo ℹ️  Installing core Flask API dependencies...
pip install -r requirements.txt

REM Check if installation was successful
if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully!
) else (
    echo ❌ Installation failed. Trying with official PyPI index...
    echo ℹ️  If you encounter version issues, try using the official PyPI index:
    echo    pip install -i https://pypi.org/simple/ -r requirements.txt
    pip install -i https://pypi.org/simple/ -r requirements.txt
    
    if %errorlevel% equ 0 (
        echo ✅ Dependencies installed successfully with official PyPI!
    ) else (
        echo ❌ Installation still failed. Please check your internet connection and Python version.
        echo 💡 Try installing packages individually:
        echo    pip install Flask Flask-SQLAlchemy Flask-Migrate psycopg2-binary python-dotenv
        pause
        exit /b 1
    )
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo ⚙️  Creating .env file...
    (
        echo # Environment variables for Provision-it Flask API
        echo # Update these values for your setup
        echo.
        echo # Database configuration
        echo DATABASE_URL=postgresql://username:password@localhost/provision_it
        echo.
        echo # Flask configuration
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo JWT_SECRET_KEY=jwt-secret-string
        echo.
        echo # Server configuration
        echo FLASK_DEBUG=True
        echo FLASK_HOST=127.0.0.1
        echo FLASK_PORT=5000
    ) > .env
    echo ✅ Created .env file with default values
) else (
    echo ℹ️  .env file already exists
)

echo.
echo 🎉 Setup complete!
echo.
echo To activate the virtual environment:
echo   venv\Scripts\activate.bat
echo.
echo To run the application:
echo   python run.py
echo.
echo To install development dependencies (optional):
echo   # Uncomment development packages in requirements.txt and run:
echo   pip install -r requirements.txt
echo.
echo Don't forget to:
echo   1. Update the DATABASE_URL in .env
echo   2. Create your PostgreSQL database
echo   3. Initialize the database tables
echo.
pause