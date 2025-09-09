# Provision-it Flask API

A Flask backend API for a real-world asset fractional ownership project.

## 🏗️ Project Structure

```
Provision-it/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── asset.py         # Asset info, history, value
│   │   ├── ledger.py        # Fraction transactions
│   │   └── user.py          # User info and ownership queries
│   └── utils.py             # Helper functions
├── templates/               # HTML templates
│   ├── base.html
│   ├── login.html
│   └── asset_history.html
├── static/                  # Static files
│   ├── css/style.css
│   └── js/app.js
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # All dependencies (production + optional dev)
├── setup_env.sh            # Automated setup script (macOS/Linux)
└── setup_env.bat           # Automated setup script (Windows)
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**For macOS/Linux:**
```bash
./setup_env.sh
```

**For Windows:**
```cmd
setup_env.bat
```

### Option 2: Manual Setup

#### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Optional: Install development dependencies
# Uncomment the development packages in requirements.txt and run:
# pip install -r requirements.txt
```

### 3. Database Setup

Make sure you have PostgreSQL running and create a database:

```sql
CREATE DATABASE provision_it;
```

Update the database URL in `config.py` or set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://username:password@localhost/provision_it"
```

### 4. Initialize Database

```bash
# Create tables
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Import your existing data (if you have CSV files)
# Use the import_postgres.sql script with your data
```

### 5. Run the Application

```bash
python run.py
```

The API will be available at `http://127.0.0.1:5000`

## 🔧 Troubleshooting

### Version Conflicts
If you encounter version conflicts during installation, try:

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
- Verify connection credentials in `.env` file
- Test connection: `psql -h localhost -U username -d provision_it`

## 📦 Dependencies

### Core Dependencies (`requirements.txt`)
- **Core Flask Framework**: Flask (>=2.3.0), Werkzeug (>=2.3.0)
- **Database**: Flask-SQLAlchemy (>=3.0.0), Flask-Migrate (>=4.0.0), psycopg2-binary (>=2.9.0)
- **Environment**: python-dotenv (>=1.0.0)
- **Data Generation**: Faker (>=20.0.0), tzdata (>=2024.0) (for existing data)
- **Production Server**: gunicorn (>=20.0.0)
- **Security**: Flask-CORS (>=4.0.0)
- **API Documentation**: flask-restx (>=1.0.0)
- **Monitoring**: Flask-Logging (>=0.1.0)

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

## 📚 API Endpoints

### Authentication

- **POST** `/api/login` - User login
  ```json
  {
    "username": "user1",
    "password": "^m&ut3&I52MT"
  }
  ```

### Assets

- **GET** `/api/assets/<asset_id>` - Get current asset info and value
- **GET** `/api/assets/<asset_id>/history` - Get historical asset value records
  - Query params: `limit` (optional, default 100)
- **GET** `/api/assets/<asset_id>/snapshot?at=YYYY-MM-DD` - Get ownership snapshot at specific date
- **GET** `/api/assets` - Get all assets (for testing)

### Users & Ownership

- **GET** `/api/owners/<user_id>/fractions` - Get all current fractions owned by user
  - Query params: `at` (optional, format: YYYY-MM-DD) - get fractions at specific date
- **GET** `/api/owners/<user_id>/portfolio` - Get user portfolio summary

### Trading & Ledger

- **POST** `/api/trade` - Create a transaction record
  ```json
  {
    "from_user_id": 1,
    "to_user_id": 2,
    "fraction_id": 123,
    "quantity": 1,
    "unit_price": 150.50,
    "currency": "USD",
    "notes": "Optional trade notes"
  }
  ```
- **GET** `/api/transactions` - Get transaction history
  - Query params: `user_id`, `asset_id`, `limit` (optional)
- **GET** `/api/transactions/<transaction_id>` - Get specific transaction details

## 🎨 Web Interface

The application includes a simple web interface:

- **Login Page**: `/login` - User authentication
- **Asset History**: `/assets` - View asset information and value history

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key for sessions
- `JWT_SECRET_KEY` - JWT token secret
- `FLASK_DEBUG` - Enable debug mode (True/False)
- `FLASK_HOST` - Host to bind to (default: 127.0.0.1)
- `FLASK_PORT` - Port to bind to (default: 5000)

### Database Models

The application uses SQLAlchemy models that match your PostgreSQL schema:

- **User** - User accounts with manager privileges
- **Asset** - Fractional assets with approval workflow
- **Fraction** - Individual fractions of assets
- **Ownership** - User ownership of fractions
- **Transaction** - Trading history and ledger
- **ValueHistory** - Historical asset values

## 🛠️ Utility Functions

The `app/utils.py` file contains helper functions:

- `calculate_fraction_value(asset_id)` - Calculate current fraction value
- `get_asset_current_value(asset_id)` - Get latest asset value
- `get_ownership_snapshot(asset_id, at_date)` - Get ownership at specific date
- `get_user_fractions_at_date(user_id, at_date)` - Get user's fractions at date
- `validate_date_format(date_string)` - Validate YYYY-MM-DD format

## 📊 Example API Usage

### Get Asset Information

```bash
curl http://127.0.0.1:5000/api/assets/1
```

Response:
```json
{
  "asset_id": 1,
  "name": "Stock 1",
  "description": "Somebody recognize free.",
  "current_value": 150000,
  "fraction_value": 15.00,
  "available_fractions": 10000,
  "status": "approved"
}
```

### Get User's Fractions

```bash
curl http://127.0.0.1:5000/api/owners/1/fractions
```

### Create a Trade

```bash
curl -X POST http://127.0.0.1:5000/api/trade \
  -H "Content-Type: application/json" \
  -d '{
    "from_user_id": 1,
    "to_user_id": 2,
    "fraction_id": 123,
    "quantity": 1,
    "unit_price": 150.50,
    "currency": "USD"
  }'
```

## 🔒 Security Notes

- Passwords are stored in plain text (for demo purposes)
- In production, implement proper password hashing
- Add JWT token authentication for API endpoints
- Implement rate limiting and input validation
- Use HTTPS in production

## 🧪 Testing

You can test the API using the provided sample data or create your own test data using the `generate.py` script.

## 📝 Development

### Adding New Routes

1. Create a new blueprint in `app/routes/`
2. Register the blueprint in `app/__init__.py`
3. Add appropriate error handling and validation

### Database Migrations

The application uses Flask-Migrate for database schema changes:

```bash
flask db init
flask db migrate -m "Description of changes"
flask db upgrade
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational/demonstration purposes.