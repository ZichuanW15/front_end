"""
Trading view for formatting trading-related responses.
"""

from flask import jsonify


class TradingView:
    """View class for trading responses."""
    
    def render_trade_success(self, result):
        """
        Render successful trade execution response.
        
        Args:
            result: Trade execution result dictionary
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'message': result['message'],
            'trade': result['trade_details'],
            'status': 'success'
        }), 201
    
    def render_asset_offers(self, offers):
        """
        Render asset offers response.
        
        Args:
            offers: Dictionary with asset offers
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'asset_id': offers['asset_id'],
            'buy_offers': offers['buy_offers'],
            'sell_offers': offers['sell_offers'],
            'buy_count': offers['buy_count'],
            'sell_count': offers['sell_count'],
            'status': 'success'
        })
    
    def render_error(self, error_message, status_code):
        """
        Render error response.
        
        Args:
            error_message: Error message
            status_code: HTTP status code
            
        Returns:
            Response: JSON error response
        """
        return jsonify({
            'error': 'Trading Error',
            'message': error_message,
            'status_code': status_code
        }), status_code