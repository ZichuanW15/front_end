"""Portfolio routes for user holdings and transaction history."""

from flask import Blueprint
from app.controllers.portfolio_controller import PortfolioController

bp = Blueprint("portfolio", __name__, url_prefix="/users")
controller = PortfolioController()


# User holdings (aggregated, grouped by asset + current valuation)
@bp.route("/<int:user_id>/fractions/owning", methods=["GET"])
def owning_fractions(user_id):
    """
    Endpoint to retrieve user's owning fractions aggregated by asset.

    Args:
        user_id: The ID of the user.

    Returns:
        JSON response with user's owning fractions.
    """
    return controller.owning_fractions(user_id)


# User-related transaction history (filterable by asset_id, with paging)
@bp.route("/<int:user_id>/transactions", methods=["GET"])
def user_transactions(user_id):
    """
    Endpoint to retrieve user's transaction history with pagination.

    Args:
        user_id: The ID of the user.

    Returns:
        JSON response with user's transactions.
    """
    return controller.user_transactions(user_id)