"""
Frontend routes for serving HTML pages.
"""

import os
from flask import Blueprint, send_from_directory, current_app, redirect, url_for

bp = Blueprint('frontend', __name__)

@bp.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """
    Serve static files from the frontend directory.
    
    Args:
        filename (str): The filename to serve
        
    Returns:
        Response: The requested file
    """
    frontend_dir = os.path.join(current_app.root_path, '..', 'frontend')
    return send_from_directory(frontend_dir, filename)

@bp.route('/')
def index():
    """
    Redirect root to login page.
    """
    return redirect('/frontend/login.html')

@bp.route('/login')
def login_redirect():
    """
    Redirect /login to /frontend/login.html
    """
    return redirect('/frontend/login.html')