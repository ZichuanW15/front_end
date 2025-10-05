from flask import Blueprint
from app.controllers.portfolio_controller import PortfolioController

bp = Blueprint("portfolio", __name__, url_prefix="/users")
controller = PortfolioController()

# User holdings (aggregated, grouped by asset + current valuation)
@bp.route("/<int:user_id>/fractions/owning", methods=["GET"])
def owning_fractions(user_id):
    return controller.owning_fractions(user_id)

# User-related transaction history (filterable by asset_id, with paging)
@bp.route("/<int:user_id>/transactions", methods=["GET"])
def user_transactions(user_id):
    return controller.user_transactions(user_id)