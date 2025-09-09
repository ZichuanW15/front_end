# Provision-it Flask API

A modern, scalable Flask application for fractional asset ownership management with a comprehensive REST API.

## 🏗️ Application Structure

```
Provision-it/
├── app/
│   ├── __init__.py              # Main app factory with error handling
│   ├── models.py                # Database models (fixed column mappings)
│   ├── utils.py                 # Utility functions
│   ├── api/                     # New API package
│   │   ├── __init__.py
│   │   ├── errors.py            # Centralized error handling
│   │   ├── decorators.py        # Common decorators
│   │   └── v1/                  # API version 1
│   │       ├── __init__.py      # V1 blueprint registration
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── assets.py        # Asset management endpoints
│   │       ├── users.py         # User/owner endpoints
│   │       └── transactions.py  # Transaction/ledger endpoints
│   └── routes/                  # Legacy routes (backward compatibility)
│       ├── auth.py
│       ├── asset.py
│       ├── user.py
│       └── ledger.py
├── templates/                   # HTML templates
│   ├── base.html
│   ├── login.html
│   └── asset_history.html
├── static/                      # Static files
│   ├── css/style.css
│   └── js/app.js
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── requirements.txt             # Dependencies
├── setup_env.sh                 # Setup script (macOS/Linux)
├── setup_env.bat                # Setup script (Windows)
└── README.md                    # This file
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**macOS/Linux:**
```bash
chmod +x setup_env.sh
./setup_env.sh
```

**Windows:**
```cmd
setup_env.bat
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env  # Edit with your database credentials

# Run the application
python run.py
```

## 📚 API Documentation

### Base URL
- **Development**: `http://127.0.0.1:5001`
- **API Documentation**: `http://127.0.0.1:5001/api`

### API Endpoints (v1)

#### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | User login |
| `POST` | `/api/v1/auth/logout` | User logout |
| `GET` | `/api/v1/auth/profile` | Get user profile |
| `GET` | `/api/v1/auth/users` | List all users |
| `GET` | `/api/v1/auth/users/<id>` | Get specific user |

#### Assets (`/api/v1/assets`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/assets/` | List all assets (paginated) |
| `GET` | `/api/v1/assets/<id>` | Get asset details |
| `GET` | `/api/v1/assets/<id>/history` | Get asset value history |
| `GET` | `/api/v1/assets/<id>/snapshot?at=YYYY-MM-DD` | Ownership snapshot |
| `GET` | `/api/v1/assets/<id>/fractions` | Get asset fractions |

#### Users (`/api/v1/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | List all users (paginated) |
| `GET` | `/api/v1/users/<id>` | Get user details |
| `GET` | `/api/v1/users/<id>/fractions` | Get user's fractions |
| `GET` | `/api/v1/users/<id>/fractions/history?at=YYYY-MM-DD` | Historical fractions |
| `GET` | `/api/v1/users/<id>/portfolio` | Complete portfolio summary |

#### Transactions (`/api/v1/transactions`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/transactions/` | List all transactions (paginated) |
| `POST` | `/api/v1/transactions/trade` | Create new trade |
| `GET` | `/api/v1/transactions/<id>` | Get transaction details |
| `GET` | `/api/v1/transactions/user/<id>` | User's transactions |
| `GET` | `/api/v1/transactions/fraction/<id>` | Fraction transactions |
| `GET` | `/api/v1/transactions/stats` | Transaction statistics |

## 🔧 Key Features

### 1. Centralized Error Handling
- Custom exception classes (`APIError`, `ValidationError`, `NotFoundError`)
- Standardized error responses
- Automatic error handling registration

### 2. Response Standardization
- Consistent success/error response format
- Proper HTTP status codes
- Structured data responses

### 3. Decorators for Common Functionality
- `@require_json` - Ensure JSON requests
- `@require_fields` - Validate required fields
- `@paginate` - Add pagination support
- `@handle_exceptions` - Automatic exception handling

### 4. API Versioning
- Clean v1 API structure
- Legacy endpoints maintained for backward compatibility
- Easy to add new versions

### 5. Database Model Fixes
- Fixed all column name mismatches
- Proper foreign key relationships
- Consistent naming conventions

## 📊 Response Format

### Success Response
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "status_code": 200,
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "status_code": 400,
  "errors": {
    // Additional error details (optional)
  }
}
```

## 🗄️ Database Configuration

### PostgreSQL Setup
1. Install PostgreSQL
2. Create database: `provision_it`
3. Update `config.py` with your credentials:
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/provision_it'
   ```

### Database Schema
The application uses the following main tables:
- `users` - User accounts
- `assets` - Asset information
- `fractions` - Fraction details
- `ownership` - User fraction ownership
- `transactions` - Trading records
- `valuehistory` - Asset value history

## 🛠️ Development

### Running in Development Mode
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Set debug mode
export FLASK_DEBUG=true   # macOS/Linux
# or
set FLASK_DEBUG=true      # Windows

# Run the application
python run.py
```

### Testing API Endpoints
```bash
# Test API documentation
curl http://127.0.0.1:5001/api

# Test authentication
curl -X POST http://127.0.0.1:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'

# Test assets
curl http://127.0.0.1:5001/api/v1/assets/
```

## 📦 Dependencies

### Core Dependencies
- **Flask** (>=2.3.0) - Web framework
- **Flask-SQLAlchemy** (>=3.0.0) - Database ORM
- **Flask-Migrate** (>=4.0.0) - Database migrations
- **psycopg2-binary** (>=2.9.0) - PostgreSQL adapter
- **python-dotenv** (>=1.0.0) - Environment variables

### Optional Development Dependencies
To install development tools, uncomment the development packages in `requirements.txt` and run:
```bash
pip install -r requirements.txt
```

**Available development packages:**
- **Testing**: pytest, pytest-flask, pytest-cov
- **Code Quality**: black, flake8, isort, pre-commit, mypy
- **Development Tools**: ipython, jupyter, notebook
- **Database Tools**: alembic
- **API Testing**: requests, httpx
- **Environment Management**: python-decouple

## 🔧 Troubleshooting

### Version Conflicts
If you encounter version conflicts during installation:

1. **Use the official PyPI index:**
   ```bash
   pip install -i https://pypi.org/simple/ -r requirements.txt
   ```

2. **Install packages individually:**
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-Migrate psycopg2-binary python-dotenv
   ```

3. **Install only core packages:**
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-Migrate psycopg2-binary python-dotenv Faker gunicorn Flask-CORS flask-restx
   ```

### Python Version Issues
- **Minimum Python version**: 3.8+
- **Recommended Python version**: 3.9+
- If using Python 3.7 or earlier, some packages may not be available

### Database Connection Issues
- Ensure PostgreSQL is running
- Check that the database exists
- Verify connection credentials in `config.py`
- Test connection: `psql -h localhost -U username -d provision_it`

### Common Issues
1. **Template not found**: Ensure templates are in the correct directory
2. **Database column errors**: Check that models match the actual database schema
3. **Import errors**: Verify virtual environment is activated

## 🔄 Backward Compatibility

Legacy endpoints are still available at `/api/legacy/` for existing integrations:
- `/api/legacy/login`
- `/api/legacy/assets/<id>`
- `/api/legacy/owners/<id>/fractions`
- `/api/legacy/trade`

## 🚀 Production Deployment

### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Environment Variables
Set the following environment variables for production:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://user:pass@host:port/db
```

## 📝 License

This project is part of the Provision-it fractional ownership platform.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions, please refer to the project documentation or contact the development team.