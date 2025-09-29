# Flask API Backbone

A minimal, modular, and extensible Flask + SQLAlchemy backend skeleton for collaborative development.

## 🎯 Features

- **Minimal Setup**: Only essential dependencies included
- **Auto-Discovery**: Automatically registers Blueprints from `app/routes/` folder
- **Database Ready**: PostgreSQL integration with SQLAlchemy
- **Schema-Based Init**: Uses SQL schema file for database initialization (like the original project)
- **Health Checks**: Built-in health monitoring endpoints
- **User Authentication**: Complete user signup, login, logout, and session management
- **User Management**: Profile updates, user deletion with authorization controls
- **Session Management**: Secure session handling with token-based authentication
- **Authorization**: Role-based access control with admin privileges
- **Testing**: Comprehensive test suite including authentication and user management tests
- **Environment Config**: `.env` file support for configuration
- **Collaborative**: Multiple developers can add features without conflicts

## 📁 Project Structure

```
provision_it_v2/
├── app/
│   ├── __init__.py            # App factory with Blueprint auto-discovery
│   ├── models.py              # SQLAlchemy models matching schema.sql
│   ├── decorators.py          # Authentication and validation decorators
│   ├── controllers/           # MVC Controllers
│   │   ├── auth_controller.py # Authentication controller
│   │   └── user_controller.py # User management controller
│   ├── services/              # MVC Services (business logic)
│   │   ├── auth_service.py    # Authentication service
│   │   └── user_service.py    # User management service
│   ├── views/                 # MVC Views (response formatting)
│   │   ├── auth_view.py       # Authentication view
│   │   └── user_view.py       # User management view
│   └── routes/                # URL routing
│       ├── auth.py            # Authentication endpoints
│       ├── users.py           # User management endpoints
│       └── health.py          # Health check endpoints
├── tests/
│   ├── test_db.py             # Database connectivity tests
│   └── test_user_api.py       # Authentication and user management tests
├── config.py                  # Configuration management
├── schema_postgres.sql        # Database schema with tables, functions, triggers
├── import_postgres.sql        # Database insert data
├── init_db_postgres.py        # Database initialization
├── run.py                     # Application entry point
├── test_auth_demo.py          # Demo script for testing auth endpoints
├── requirements.txt           # Dependencies
├── .env                       # Environment configuration template
├── setup_env.sh               # Automated setup script for Unix/Linux/macOS
├── setup_env.bat              # Automated setup script for Windows
└── README.md                  # This file
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

#### For Unix/Linux/macOS:
```bash
# Clone or copy the provision_it_v2 directory
cd provision_it_v2

# Run the automated setup script
./setup_env.sh
```

#### For Windows:
```cmd
REM Clone or copy the provision_it_v2 directory
cd provision_it_v2

REM Run the automated setup script
setup_env.bat
```

The setup scripts will automatically:
- ✅ Check Python version (3.8+ required)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ **Create .env file with database configuration** (interactive prompts)
- ✅ Generate secure secret key automatically
- ✅ Interactive database configuration prompts
- ✅ Test database connection (if configured)
- ✅ Initialize database (optional)
- ✅ Run tests (optional)

### Option 2: Manual Setup

#### 1. Setup Environment

```bash
# Clone or copy the provision_it_v2 directory
cd provision_it_v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Database

```bash
# Create/Edit .env file with your database settings
# DATABASE_URL=postgresql://username:password@localhost:5432/api_backbone

# OR use the automated setup scripts which create .env interactively
```

#### 3. Initialize Database

```bash
# 1. Create database
createdb your_database_name

# 2. Run initialization
python init_db_postgres.py

# 3. Delete database
dropdb your_database_name

# 3.1 kill all database connection of database
psql -U your_username -d postgres

-- Kill all connections to your_database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'provision_it_v2'
  AND pid <> pg_backend_pid();
```

#### 4. Run the Application

```bash
# Development server
python run.py

# Or using Flask CLI
flask run
```

The API will be available at `http://127.0.0.1:5001`

## 🔧 Interactive .env Configuration

When you run the setup scripts, they will prompt you for database configuration:

```
[INFO] Configuring database settings...
Database host [localhost]: 
Database port [5432]: 
Database name [provision_it_v2]: 
Database user [postgres]: 
Database password: 
[SUCCESS] .env file created with database configuration
[INFO] Database URL: postgresql://postgres:***@localhost:5432/provision_it_v2
```

**Features:**
- ✅ **Default values** provided for all fields (just press Enter to use defaults)
- ✅ **Secure password input** (password is hidden while typing)
- ✅ **Automatic secret key generation** using Python's `secrets` module
- ✅ **Complete .env file creation** with all necessary variables
- ✅ **Backup existing .env** files automatically

## 🔍 Health Checks

The application includes several health check endpoints:

- `GET /health` - Basic health status
- `GET /health/db` - Database connectivity check
- `GET /health/detailed` - Comprehensive system status

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_db.py
```

## 🗄️ Database Initialization

The API backbone uses the same database initialization approach as the original project:

### Schema-Based Initialization

Instead of using `db.create_all()`, the backbone executes the `schema_postgres.sql` file which includes:

- **Tables**: Users, Assets, Fractions, Ownership, Transactions, ValueHistory
- **Functions**: Manager approval checks, fraction value calculations
- **Triggers**: Automatic fraction value updates, manager approval validation
- **Indexes**: Performance optimization indexes

### Database Schema

The schema includes the complete fractional ownership platform structure:

- **Users**: Authentication and authorization
- **Assets**: Fractional ownership assets
- **Fractions**: Individual asset fractions
- **Transactions**: Fraction trading records

## 🔧 Adding New Features

### Adding New API Routes

1. Create a new Python file in `app/routes/` (e.g., `users.py`)
2. Define a Blueprint named `bp`:

```python
from flask import Blueprint, jsonify
from app.models import User

bp = Blueprint('users', __name__)

@bp.route('/users')
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@bp.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
```

3. The Blueprint will be automatically discovered and registered!

### Adding New Models

The models in `app/models.py` already match the schema structure. To add new models:

1. Add the table to `schema_postgres.sql`
2. Add the corresponding SQLAlchemy model to `app/models.py`
3. Update the `init_db` process if needed

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Debug mode | `true` |
| `FLASK_HOST` | Server host | `127.0.0.1` |
| `FLASK_PORT` | Server port | `5001` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost/api_backbone` |

### Configuration Classes

- `DevelopmentConfig` - Development settings
- `ProductionConfig` - Production settings  
- `TestingConfig` - Testing settings

## 🤝 Collaborative Development

### For New Team Members

1. **Clone the repository**
2. **Copy `.env.example` to `.env`** and configure your database
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Initialize database**: `flask init-db`
5. **Run tests**: `pytest` to verify setup
6. **Start development**: `python run.py`

### Adding Features

- **New APIs**: Drop a `.py` file in `app/routes/` with a Blueprint named `bp`
- **New Models**: Add to `app/models.py` and update `schema_postgres.sql`
- **New Tests**: Add to `tests/` directory
- **No core file changes needed** for new API routes!

## 📝 API Documentation

### Authentication Endpoints

#### POST /api/auth/signup
Create a new user account.

**Request Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com", 
  "password": "password123",
  "is_manager": false
}
```

**Response (201):**
```json
{
  "user": {
    "user_id": 1,
    "user_name": "testuser",
    "email": "test@example.com",
    "is_manager": false,
    "created_at": "2024-01-01T00:00:00"
  },
  "session": {
    "user_id": 1,
    "username": "testuser",
    "session_token": "abc123...",
    "is_admin": false
  },
  "message": "User registered successfully",
  "status": "success"
}
```

#### POST /api/auth/login
Authenticate user and create session.

**Request Body:**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "user": {
    "user_id": 1,
    "user_name": "testuser",
    "email": "test@example.com",
    "is_manager": false,
    "created_at": "2024-01-01T00:00:00"
  },
  "session": {
    "user_id": 1,
    "username": "testuser", 
    "session_token": "abc123...",
    "is_admin": false
  },
  "message": "Login successful",
  "status": "success"
}
```

#### POST /api/auth/logout
Logout current user and clear session.

**Response (200):**
```json
{
  "message": "Logout successful",
  "status": "success"
}
```

#### GET /api/auth/me
Get current logged-in user information.

**Response (200):**
```json
{
  "user": {
    "user_id": 1,
    "user_name": "testuser",
    "email": "test@example.com",
    "is_manager": false,
    "created_at": "2024-01-01T00:00:00"
  },
  "status": "success"
}
```

### User Management Endpoints

#### PUT /api/users/{user_id}
Update user profile. Requires authentication and ownership or admin privileges.

**Request Body:**
```json
{
  "user_name": "newusername",
  "email": "newemail@example.com",
  "password": "newpassword123"
}
```

**Response (200):**
```json
{
  "user": {
    "user_id": 1,
    "user_name": "newusername",
    "email": "newemail@example.com",
    "is_manager": false,
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "User updated successfully",
  "status": "success"
}
```

#### DELETE /api/users/{user_id}
Delete user account. Requires authentication and ownership or admin privileges.

**Response (200):**
```json
{
  "message": "User deleted successfully",
  "status": "success"
}
```

### Health Endpoints

#### GET /health
Basic health check.

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_user_api.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app
```

### Test Demo Script

A demo script is included to test the authentication endpoints:

```bash
# Make sure the Flask server is running first
python run.py

# In another terminal, run the demo
python test_auth_demo.py
```

The demo script will test:
- User signup (including duplicate validation)
- User login and session creation
- Profile updates
- Authorization checks
- Logout functionality
- Error handling

### Test Coverage

The test suite covers:
- ✅ User signup with validation
- ✅ User login and authentication
- ✅ Session management
- ✅ Profile updates with authorization
- ✅ User deletion with authorization
- ✅ Admin privilege checks
- ✅ Error handling and edge cases
- ✅ Unauthorized access prevention

## 🐛 Troubleshooting

### Database Connection Issues

1. **Check PostgreSQL is running**: `pg_ctl status`
2. **Verify connection string**: Check `DATABASE_URL` in `.env`
3. **Test connection**: `psql $DATABASE_URL`
4. **Check firewall**: Ensure port 5432 is accessible

### Schema Initialization Issues

1. **Check schema.sql exists**: `ls -la schema_postgres.sql`
2. **Verify SQL syntax**: Test with `psql -f schema_postgres.sql`
3. **Check permissions**: Ensure database user has CREATE privileges
4. **Review logs**: Check Flask application logs for SQL errors

### Import Errors

1. **Activate virtual environment**: `source venv/bin/activate`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Check Python path**: Ensure you're in the project root

### Blueprint Not Registered

1. **Check file name**: Must end with `.py`
2. **Check Blueprint name**: Must be named `bp`
3. **Check syntax**: No import errors in the file
4. **Restart server**: Blueprints are loaded at startup

## 🔄 Migration from Original Project

This backbone is designed to be compatible with the original Provision-it project:

1. **Same Schema**: Uses identical database structure
2. **Same Models**: SQLAlchemy models match the original
3. **Same Functions**: PostgreSQL functions and triggers included
4. **Same Data**: Can import existing CSV data using the same process

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Add tests for new functionality
5. Submit a pull request

---

**Happy coding! 🚀**