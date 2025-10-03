from flask import Blueprint, jsonify


bp = Blueprint("test", __name__)

@bp.route("/")
def index():
    return jsonify({"message": "Testing API is running 🚀"})
