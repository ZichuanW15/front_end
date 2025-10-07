"""
Trading routes Blueprint for trade execution.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.trading_controller import TradingController

# Create Blueprint instance
bp = Blueprint('trading', __name__, url_prefix='/trading')

# Initialize controller
trading_controller = TradingController()


@bp.route('/execute', methods=['POST'])
def execute_trade():
    """
    Execute a trade where a user accepts an existing offer.
    
    Request body:
    {
        "offer_id": 1,
        "user_id": 2
    }
    
    Returns:
        JSON response with trade execution result
    """
    return trading_controller.execute_trade()


@bp.route('/offers/<int:asset_id>', methods=['GET'])
def get_asset_offers(asset_id):
    """
    Get all active buy and sell offers for an asset.
    
    Args:
        asset_id: Asset ID
    
    Returns:
        JSON response with buy and sell offers
    """
    return trading_controller.get_asset_offers(asset_id)