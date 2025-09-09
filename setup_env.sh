#!/bin/bash

# Setup script for Provision-it Flask API
# This script creates a virtual environment and installs dependencies

set -e  # Exit on any error

echo "🚀 Setting up Provision-it Flask API environment..."

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
echo "ℹ️  Installing core Flask API dependencies..."
pip install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Installation failed. Trying with official PyPI index..."
    echo "ℹ️  If you encounter version issues, try using the official PyPI index:"
    echo "   pip install -i https://pypi.org/simple/ -r requirements.txt"
    pip install -i https://pypi.org/simple/ -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully with official PyPI!"
    else
        echo "❌ Installation still failed. Please check your internet connection and Python version."
        echo "💡 Try installing packages individually:"
        echo "   pip install Flask Flask-SQLAlchemy Flask-Migrate psycopg2-binary python-dotenv"
        exit 1
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
# Environment variables for Provision-it Flask API
# Update these values for your setup

# Database configuration
DATABASE_URL=postgresql://username:password@localhost/provision_it

# Flask configuration
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-string

# Server configuration
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
EOF
    echo "✅ Created .env file with default values"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python run.py"
echo ""
echo "To install development dependencies (optional):"
echo "  # Uncomment development packages in requirements.txt and run:"
echo "  pip install -r requirements.txt"
echo ""
echo "Don't forget to:"
echo "  1. Update the DATABASE_URL in .env"
echo "  2. Create your PostgreSQL database"
echo "  3. Initialize the database tables"