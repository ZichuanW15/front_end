"""Portfolio view for rendering portfolio-related responses."""

from typing import List, Dict, Any
from flask import jsonify
from app.models import Transaction


class PortfolioView:
    """View class for rendering portfolio responses."""

    def render_owning(self, user_id: int, items: List[Dict[str, Any]]):
        """
        Render user's owning fractions response.

        Args:
            user_id: The ID of the user.
            items: List of owning fraction data.

        Returns:
            JSON response with user's owning fractions.
        """
        return jsonify({
            "user_id": user_id,
            "count": len(items),
            "items": items,
            "status": "success",
        })

    def render_user_transactions(
        self,
        user_id: int,
        items: List[Transaction],
        pagination: Dict[str, int]
    ):
        """
        Render user's transaction history response.

        Args:
            user_id: The ID of the user.
            items: List of Transaction objects.
            pagination: Dict with 'total', 'page', and 'per_page' keys.

        Returns:
            JSON response with user's transactions.
        """
        return jsonify({
            "user_id": user_id,
            "page": pagination["page"],
            "per_page": pagination["per_page"],
            "total": pagination["total"],
            "items": [t.to_dict() for t in items],
            "status": "success",
        })

    def render_error(self, message: str, status_code: int):
        """
        Render error response.

        Args:
            message: Error message.
            status_code: HTTP status code.

        Returns:
            JSON response with error details and status code.
        """
        return jsonify({
            "error": "Portfolio Error",
            "message": message,
            "status_code": status_code,
        }), status_code