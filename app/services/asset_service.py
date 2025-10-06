"""
Asset service for asset-related business logic.
"""

from app import db
from app.models import Asset
from datetime import datetime
from typing import Optional, List, Dict, Any


class AssetService:
    """Service class for asset operations."""
    
    @staticmethod
    def create_asset(asset_data: Dict[str, Any]) -> Asset:
        """
        Create a new asset.
        
        Args:
            asset_data: Dictionary containing asset information
            
        Returns:
            Asset: Created asset instance
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['asset_name', 'total_unit', 'unit_min', 'unit_max', 'total_value']
        for field in required_fields:
            if field not in asset_data or asset_data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        asset = Asset(
            asset_name=asset_data['asset_name'],
            total_unit=asset_data['total_unit'],
            unit_min=asset_data['unit_min'],
            unit_max=asset_data['unit_max'],
            total_value=asset_data['total_value'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(asset)
        db.session.commit()
        return asset
    
    @staticmethod
    def get_asset_by_id(asset_id: int) -> Optional[Asset]:
        """
        Get asset by ID.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Asset or None if not found
        """
        return Asset.query.get(asset_id)
    
    @staticmethod
    def get_all_assets(page: int = 1, per_page: int = 20) -> List[Asset]:
        """
        Get all assets with pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            List of Asset objects
        """
        # If per_page is less than or equal to 0, return all assets (no pagination)
        if per_page is not None and per_page <= 0:
            return Asset.query.all()

        return Asset.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        ).items
    
    @staticmethod
    def update_asset(asset_id: int, asset_data: Dict[str, Any]) -> Optional[Asset]:
        """
        Update asset information.
        
        Args:
            asset_id: Asset ID
            asset_data: Dictionary containing updated asset information
            
        Returns:
            Updated Asset or None if not found
        """
        asset = Asset.query.get(asset_id)
        if not asset:
            return None
        
        # Update allowed fields
        allowed_fields = ['asset_name', 'total_unit', 'unit_min', 'unit_max', 'total_value']
        for field in allowed_fields:
            if field in asset_data:
                setattr(asset, field, asset_data[field])
        
        db.session.commit()
        return asset
    
    @staticmethod
    def delete_asset(asset_id: int) -> bool:
        """
        Delete an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            True if deleted, False if not found
        """
        asset = Asset.query.get(asset_id)
        if not asset:
            return False
        
        db.session.delete(asset)
        db.session.commit()
        return True
    
    @staticmethod
    def get_asset_fractions(asset_id: int) -> List:
        """
        Get all fractions for an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            List of Fraction objects
        """
        asset = Asset.query.get(asset_id)
        if not asset:
            return []
        
        return asset.fractions