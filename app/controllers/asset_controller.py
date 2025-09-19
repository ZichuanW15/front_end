"""
Asset controller for handling asset-related requests.
"""

from flask import request
from app.services.asset_service import AssetService
from app.views.asset_view import AssetView


class AssetController:
    """Controller for asset operations."""
    
    def __init__(self):
        self.asset_service = AssetService()
        self.asset_view = AssetView()
    
    def create_asset(self):
        """
        Handle asset creation request.
        
        Returns:
            Response: JSON response with created asset data
        """
        try:
            asset_data = request.get_json()
            if not asset_data:
                return self.asset_view.render_error("No JSON data provided", 400)
            
            asset = self.asset_service.create_asset(asset_data)
            return self.asset_view.render_asset_created(asset)
        except ValueError as e:
            return self.asset_view.render_error(str(e), 400)
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)
    
    def get_asset(self, asset_id):
        """
        Handle get asset by ID request.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Response: JSON response with asset data
        """
        try:
            asset = self.asset_service.get_asset_by_id(asset_id)
            if not asset:
                return self.asset_view.render_error("Asset not found", 404)
            
            return self.asset_view.render_asset(asset)
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)
    
    def get_assets(self):
        """
        Handle get all assets request.
        
        Returns:
            Response: JSON response with assets list
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            assets = self.asset_service.get_all_assets(page, per_page)
            return self.asset_view.render_assets_list(assets)
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)
    
    def update_asset(self, asset_id):
        """
        Handle asset update request.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Response: JSON response with updated asset data
        """
        try:
            asset_data = request.get_json()
            if not asset_data:
                return self.asset_view.render_error("No JSON data provided", 400)
            
            asset = self.asset_service.update_asset(asset_id, asset_data)
            if not asset:
                return self.asset_view.render_error("Asset not found", 404)
            
            return self.asset_view.render_asset_updated(asset)
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)
    
    def delete_asset(self, asset_id):
        """
        Handle asset deletion request.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Response: JSON response with deletion status
        """
        try:
            success = self.asset_service.delete_asset(asset_id)
            if not success:
                return self.asset_view.render_error("Asset not found", 404)
            
            return self.asset_view.render_asset_deleted()
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)
    
    def get_asset_fractions(self, asset_id):
        """
        Handle get asset fractions request.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Response: JSON response with fractions list
        """
        try:
            fractions = self.asset_service.get_asset_fractions(asset_id)
            return self.asset_view.render_asset_fractions(fractions)
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)