from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)
    
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