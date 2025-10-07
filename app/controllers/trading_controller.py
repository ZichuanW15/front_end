"""
Trading controller for handling trade execution requests.
"""

from flask import request
from app.services.trading_service import TradingService
from app.views.trading_view import TradingView
from app.controllers.base_controller import BaseController


class TradingController(BaseController):
    """Controller for trading operations."""
    
    def __init__(self):
        self.service = TradingService()
        self.view = TradingView()
    
    def execute_trade(self):
        """
        Execute a trade where a user accepts an existing offer.
        
        Request body:
        {
            "offer_id": 1,
            "user_id": 2
        }
        
        Returns:
            Response: JSON response with trade execution result
        """
        def _execute():
            data = request.get_json()
            if not data:
                return self.view.render_error("No JSON data provided", 400)
            
            offer_id = data.get('offer_id')
            user_id = data.get('user_id')
            
            if not offer_id or not user_id:
                return self.view.render_error("Missing offer_id or user_id", 400)
            
            result = self.service.execute_trade(offer_id, user_id)
            return self.view.render_trade_success(result)
        return self.handle_request(_execute)
    
    def get_asset_offers(self, asset_id):
        """
        Get all active buy and sell offers for an asset.
        
        Args:
            asset_id: Asset ID
        
        Returns:
            Response: JSON response with buy and sell offers
        """
        try:
            offers = self.service.get_asset_offers(asset_id)
            return self.view.render_asset_offers(offers)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)