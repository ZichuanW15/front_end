"""Portfolio controller for handling user portfolio and transaction endpoints."""

from flask import request
from app.services.portfolio_service import PortfolioService
from app.views.portfolio_view import PortfolioView


class PortfolioController:
    """Controller for managing user portfolio operations."""

    def __init__(self):
        self.service = PortfolioService()
        self.view = PortfolioView()

    def owning_fractions(self, user_id: int):
        """
        Get user's owning fractions aggregated by asset.

        Args:
            user_id: The ID of the user.

        Returns:
            JSON response with user's owning fractions or error message.
        """
        try:
            data = self.service.user_owning_fractions(user_id)
            return self.view.render_owning(user_id, data)
        except Exception as e:
            return self.view.render_error(str(e), 500)

    def user_transactions(self, user_id: int):
        """
        Get user's transaction history with pagination and optional filtering.

        Args:
            user_id: The ID of the user.

        Returns:
            JSON response with user's transactions or error message.
        """
        try:
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 20, type=int)
            asset_id = request.args.get("asset_id", type=int)

            items, total = self.service.user_transactions(
                user_id=user_id,
                asset_id=asset_id,
                page=page,
                per_page=per_page,
            )
            pagination = {"total": total, "page": page, "per_page": per_page}
            return self.view.render_user_transactions(user_id, items, pagination)
        except Exception as e:
            return self.view.render_error(str(e), 500)