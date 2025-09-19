"""
Asset view for formatting asset-related responses.
"""

from flask import jsonify


class AssetView:
    """View class for asset responses."""
    
    def render_asset(self, asset):
        """
        Render single asset response.
        
        Args:
            asset: Asset model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'asset': asset.to_dict(),
            'status': 'success'
        })
    
    def render_asset_created(self, asset):
        """
        Render asset creation response.
        
        Args:
            asset: Created Asset model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'asset': asset.to_dict(),
            'message': 'Asset created successfully',
            'status': 'success'
        }), 201
    
    def render_asset_updated(self, asset):
        """
        Render asset update response.
        
        Args:
            asset: Updated Asset model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'asset': asset.to_dict(),
            'message': 'Asset updated successfully',
            'status': 'success'
        })
    
    def render_asset_deleted(self):
        """
        Render asset deletion response.
        
        Returns:
            Response: JSON response
        """
        return jsonify({
            'message': 'Asset deleted successfully',
            'status': 'success'
        })
    
    def render_assets_list(self, assets):
        """
        Render assets list response.
        
        Args:
            assets: List of Asset model instances
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'assets': [asset.to_dict() for asset in assets],
            'count': len(assets),
            'status': 'success'
        })
    
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
            'error': 'Asset Error',
            'message': error_message,
            'status_code': status_code
        }), status_code