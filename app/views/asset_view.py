"""
Asset view for formatting asset-related responses.
"""

from flask import jsonify
from .base_view import BaseView


class AssetView(BaseView):
    """View class for asset responses."""
    
    def __init__(self):
        """Initialize AssetView with entity name."""
        super().__init__('Asset')
    
    def render_asset(self, asset):
        """
        Render single asset response.
        
        Args:
            asset: Asset model instance
            
        Returns:
            Response: JSON response
        """
        return self.render_single(asset)
    
    def render_asset_created(self, asset):
        """
        Render asset creation response.
        
        Args:
            asset: Created Asset model instance
            
        Returns:
            Response: JSON response
        """
        return self.render_created(asset)
    
    def render_asset_updated(self, asset):
        """
        Render asset update response.
        
        Args:
            asset: Updated Asset model instance
            
        Returns:
            Response: JSON response
        """
        return self.render_updated(asset)
    
    def render_asset_deleted(self):
        """
        Render asset deletion response.
        
        Returns:
            Response: JSON response
        """
        return self.render_deleted()
    
    def render_assets_list(self, assets):
        """
        Render assets list response.
        
        Args:
            assets: List of Asset model instances
            
        Returns:
            Response: JSON response
        """
        return self.render_list(assets, 'assets')
    
    def render_asset_fractions(self, fractions):
        """
        Render asset fractions response.
        
        Args:
            fractions: List of Fraction model instances
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'fractions': [fraction.to_dict() for fraction in fractions],
            'count': len(fractions),
            'status': 'success'
        })
    
    # New methods for asset value history
    def render_value_history(self, items, asset_id):
        return jsonify({
            "asset_id": asset_id,
            "count": len(items),
            "items": [it.to_dict() for it in items],
            "status": "success",
        })
    # New method to render adjustment creation response
    def render_adjustment_created(self, row):
        data = row.to_dict()
        return jsonify({"status": "created", "item": data}), 201
    
    def render_asset_with_fraction_created(self, result):
        """
        Render asset creation with initial fraction response.
        
        Args:
            result: Dictionary containing asset, fraction, and value_history
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'asset': result['asset'].to_dict(),
            'fraction': result['fraction'].to_dict(),
            'value_history': result['value_history'].to_dict(),
            'message': 'Asset created successfully with initial fraction and value history',
            'status': 'success'
        }), 201