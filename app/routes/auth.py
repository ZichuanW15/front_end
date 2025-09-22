<<<<<<< HEAD
"""
Authentication routes Blueprint for user authentication.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.auth_controller import AuthController

# Create Blueprint instance
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize controller
auth_controller = AuthController()


@bp.route('/signup', methods=['POST'])
def signup():
    """
    User registration endpoint.
    
    Returns:
        JSON response with created user data and session info
    """
    return auth_controller.signup()


@bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Returns:
        JSON response with user data and session info
    """
    return auth_controller.login()


@bp.route('/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.
    
    Returns:
        JSON response with logout confirmation
    """
    return auth_controller.logout()


@bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current logged-in user information.
    
    Returns:
        JSON response with current user data
    """
    return auth_controller.get_current_user()
=======
# app/routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from app.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

def find_user_by_login(login):
    # 支持用邮箱或用户名登录
    if login and "@" in login:
        return User.query.filter_by(email=login.strip().lower()).first()
    return User.query.filter_by(user_name=login.strip()).first()

@bp.post("/register")
def register():
    data = request.get_json() or {}
    user_name = (data.get("user_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not user_name or not email or not password:
        return jsonify({"ok": False, "error": "user_name, email, password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"ok": False, "error": "email already registered"}), 409
    if User.query.filter_by(user_name=user_name).first():
        return jsonify({"ok": False, "error": "user_name already taken"}), 409

    # 创建用户，设置必需的字段
    u = User(
        user_name=user_name, 
        email=email,
        password=password,  # 存储明文密码（生产环境应该哈希）
        created_at=datetime.utcnow(),
        is_manager=False  # 默认为普通用户
    )
    
    db.session.add(u)
    try:
        db.session.commit()
        return jsonify({"ok": True, "message": "registered", "user_id": u.user_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"Database error: {str(e)}"}), 500

@bp.post("/login")
def login():
    data = request.get_json() or {}
    login_id = (data.get("login") or "").strip()   # 可以是 user_name 或 email
    password = data.get("password") or ""
    if not login_id or not password:
        return jsonify({"ok": False, "error": "login and password required"}), 400

    u = find_user_by_login(login_id)
    if not u:
        return jsonify({"ok": False, "error": "invalid credentials"}), 401

    # 兼容两种存储：优先 password_hash，没有就比对 password 明文
    verified = False
    if getattr(u, "password_hash", None):
        try:
            verified = check_password_hash(u.password_hash, password)
        except Exception:
            verified = False
    elif getattr(u, "password", None) is not None:
        verified = (u.password == password)

    if not verified:
        return jsonify({"ok": False, "error": "invalid credentials"}), 401

    # 极简：不发 token，前端拿到 ok=True 就跳转
    return jsonify({"ok": True, "user": {
        "user_id": u.user_id,
        "user_name": u.user_name,
        "email": u.email
    }})
>>>>>>> newrepo/frontend
