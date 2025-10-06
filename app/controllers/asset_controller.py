"""
Asset controller for handling asset-related requests.
"""

from flask import request
from app.services.asset_service import AssetService
from app.views.asset_view import AssetView
from datetime import datetime
from app.services.asset_value_service import AssetValueService


class AssetController:
    """Controller for asset operations."""
    
    def __init__(self):
        self.asset_service = AssetService()
        self.asset_view = AssetView()
        self.asset_value_service = AssetValueService()
    
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
        
    # Get the history of an asset
    def get_asset_values(self, asset_id):
        try:
            p_from = request.args.get("from")
            p_to   = request.args.get("to")
            
            # original code
            # parse  = lambda s: datetime.fromisoformat(s) if s else None
            # function to handle both simple datetime format and ISO 8601 format
            def parse_date(s):
                if not s:
                    return None
                try:
                    # Handle database format: YYYY-MM-DD HH:MM:SS.mmm (with milliseconds)
                    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    try:
                        # Handle simple format: YYYY-MM-DD HH:MM:SS (no milliseconds)
                        return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            # Handle ISO 8601 format with timezone (Z suffix)
                            # "2025-09-29T14:45:43.752Z" → "2025-09-29T14:45:43.752+00:00"
                            if s.endswith('Z'):
                                s = s[:-1] + '+00:00'
                            return datetime.fromisoformat(s)
                        except ValueError:
                            # Final fallback to simple format without timezone
                            return datetime.fromisoformat(s.replace('Z', ''))

            items = self.asset_value_service.list_history(
                # asset_id, parse(p_from), parse(p_to)
                asset_id, parse_date(p_from), parse_date(p_to)
            )
            return self.asset_view.render_value_history(items, asset_id)
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)
    
    # Administrators can manually adjust asset values
    def adjust_asset_value(self, asset_id):
        try:
            data = request.get_json()
            if not data:
                return self.asset_view.render_error("No JSON data provided", 400)
            try:
                value = float(data.get("value"))
            except (TypeError, ValueError):
                return self.asset_view.render_error("value must be a number", 400)

            adjusted_by = data.get("adjusted_by")
            if not adjusted_by:
                return self.asset_view.render_error("adjusted_by is required for now", 400)

            recorded_at = data.get("recorded_at")
            recorded_at = datetime.fromisoformat(recorded_at) if recorded_at else None
            reason = data.get("reason") or "manual adjust"

            row = self.asset_value_service.add_adjustment(
                asset_id=asset_id,
                value=value,
                adjusted_by=adjusted_by,
                reason=reason,
                recorded_at=recorded_at,
            )
            return self.asset_view.render_adjustment_created(row)
        except PermissionError as e:
            return self.asset_view.render_error(str(e), 403)
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)
    
    def create_asset_with_initial_fraction(self):
        """
        Handle complete asset creation workflow with initial fraction and value history.
        This is the admin endpoint for creating assets with all necessary components.
        
        Returns:
            Response: JSON response with created asset, fraction, and value history data
        """
        try:
            data = request.get_json()
            if not data:
                return self.asset_view.render_error("No JSON data provided", 400)
            
            # Extract asset data, owner_id, and adjusted_by
            asset_data = {k: v for k, v in data.items() if k not in ['owner_id', 'adjusted_by']}
            owner_id = data.get('owner_id')
            adjusted_by = data.get('adjusted_by')
            
            if not owner_id:
                return self.asset_view.render_error("owner_id is required", 400)
            
            if not adjusted_by:
                return self.asset_view.render_error("adjusted_by is required", 400)
            
            # Create asset with initial fraction and value history
            result = self.asset_service.create_asset_with_initial_fraction(asset_data, owner_id, adjusted_by)
            
            return self.asset_view.render_asset_with_fraction_created(result)
            
        except ValueError as e:
            return self.asset_view.render_error(str(e), 400)
        except Exception as e:
            return self.asset_view.render_error(str(e), 500)