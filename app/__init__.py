from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)
    
    # Configure session settings
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register error handlers
    from app.api.errors import register_error_handlers
    register_error_handlers(app)
    
    # Register API blueprints
    from app.api.v1 import bp as api_v1_bp
    app.register_blueprint(api_v1_bp)
    
    # Legacy API routes (for backward compatibility)
    from app.routes.auth import bp as legacy_auth_bp
    app.register_blueprint(legacy_auth_bp, url_prefix='/api/legacy')
    
    from app.routes.asset import bp as legacy_asset_bp
    app.register_blueprint(legacy_asset_bp, url_prefix='/api/legacy')
    
    from app.routes.user import bp as legacy_user_bp
    app.register_blueprint(legacy_user_bp, url_prefix='/api/legacy')
    
    from app.routes.ledger import bp as legacy_ledger_bp
    app.register_blueprint(legacy_ledger_bp, url_prefix='/api/legacy')
    
    # Template routes
    @app.route('/')
    def index():
        return render_template('login.html')
    
    @app.route('/login')
    def login_page():
        return render_template('login.html')
    
    @app.route('/assets')
    def assets_page():
        return render_template('asset_history.html')
    
    @app.route('/dashboard')
    def dashboard():
        from flask import session, redirect, url_for
        from app.models import User, Asset, Fraction, Ownership, ValueHistory
        from sqlalchemy import func, desc
        
        # Check if user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        
        user_id = session['user_id']
        
        # Query all assets where the current user owns fractions
        user_holdings = db.session.query(
            Asset.asset_id,
            Asset.name,
            Asset.description,
            Asset.available_fractions,
            func.count(Ownership.fractions_fraction_id).label('fractions_owned'),
            func.max(ValueHistory.asset_value).label('latest_asset_value'),
            func.max(Ownership.acquired_at).label('latest_purchase_date')
        ).join(
            Fraction, Asset.asset_id == Fraction.assets_asset_id
        ).join(
            Ownership, Fraction.fraction_id == Ownership.fractions_fraction_id
        ).outerjoin(
            ValueHistory, Asset.asset_id == ValueHistory.assets_asset_id
        ).filter(
            Ownership.users_user_id == user_id
        ).group_by(
            Asset.asset_id, Asset.name, Asset.description, Asset.available_fractions
        ).all()
        
        # Process holdings data
        holdings_data = []
        for holding in user_holdings:
            # Calculate fraction value using the database function logic
            if holding.latest_asset_value and holding.available_fractions and holding.available_fractions > 0:
                fraction_value = float(holding.latest_asset_value) / holding.available_fractions
            else:
                fraction_value = 0.0
            
            # Calculate total holding value
            total_value = fraction_value * holding.fractions_owned
            
            holdings_data.append({
                'asset_id': holding.asset_id,
                'name': holding.name,
                'description': holding.description,
                'fractions_owned': holding.fractions_owned,
                'latest_asset_value': holding.latest_asset_value or 0,
                'fraction_value': round(fraction_value, 2),
                'total_value': round(total_value, 2),
                'latest_purchase_date': holding.latest_purchase_date
            })
        
        return render_template('dashboard.html', holdings=holdings_data, user_id=user_id)
    
    # API documentation route
    @app.route('/api')
    def api_docs():
        return {
            'message': 'Provision-it API',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/v1/auth',
                'assets': '/api/v1/assets',
                'users': '/api/v1/users',
                'transactions': '/api/v1/transactions'
            },
            'legacy_endpoints': '/api/legacy'
        }
    
    return app