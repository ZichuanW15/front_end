from typing import List, Dict, Any
from flask import jsonify
from app.models import Transaction

class PortfolioView:
    def render_owning(self, user_id: int, items: List[Dict[str, Any]]):
        return jsonify({
            "user_id": user_id,
            "count": len(items),
            "items": items,
            "status": "success",
        })

    def render_user_transactions(self, user_id: int, items: List[Transaction], total: int, page: int, per_page: int):
        return jsonify({
            "user_id": user_id,
            "page": page,
            "per_page": per_page,
            "total": total,
            "items": [t.to_dict() for t in items],
            "status": "success",
        })

    def render_error(self, message: str, status_code: int):
        return jsonify({
            "error": "Portfolio Error",
            "message": message,
            "status_code": status_code,
        }), status_code