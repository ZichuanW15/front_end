"""
Asset service for asset-related business logic.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.database import db
from app.models import Asset, Fraction, AssetValueHistory, User


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
            ValueError: If required fields are missing or invalid
        """
        required_fields = ['asset_name', 'total_unit', 'unit_min', 'unit_max', 'total_value']
        for field in required_fields:
            if field not in asset_data or asset_data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate units constraints
        total_unit = asset_data['total_unit']
        unit_min = asset_data['unit_min']
        unit_max = asset_data['unit_max']
        
        if unit_min < 1:
            raise ValueError("unit_min must be at least 1")
        
        if unit_max < unit_min:
            raise ValueError("unit_max cannot be less than unit_min")
        
        if unit_min > total_unit:
            raise ValueError("unit_min cannot be greater than total_unit")
        
        asset = Asset(
            asset_name=asset_data['asset_name'],
            asset_description=asset_data.get('asset_description'),
            total_unit=total_unit,
            unit_min=unit_min,
            unit_max=unit_max,
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
        allowed_fields = ['asset_name', 'asset_description', 'total_unit', 'unit_min', 'unit_max', 'total_value']
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
    
    @staticmethod
    def create_asset_with_initial_fraction(asset_data: Dict[str, Any], owner_id: int, admin_user_id: int = None) -> Dict[str, Any]:
        """
        Create a new asset with initial fraction and value history record.
        This is the complete workflow for admin asset creation.
        
        Args:
            asset_data: Dictionary containing asset information
            owner_id: User ID who will own the initial fraction
            admin_user_id: User ID of the admin creating the asset (optional)
            
        Returns:
            Dictionary containing created asset and fraction data
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate owner exists
        owner = User.query.get(owner_id)
        if not owner:
            raise ValueError("Owner user not found")
        
        # Validate admin user exists and is a manager
        if admin_user_id:
            admin_user = User.query.get(admin_user_id)
            if not admin_user:
                raise ValueError("Admin user not found")
            if not admin_user.is_manager:
                raise PermissionError("Only managers can create assets")
        
        # Create the asset first
        asset = AssetService.create_asset(asset_data)
        
        try:
            # Calculate value per unit
            total_value = float(asset_data['total_value'])
            total_unit = asset_data['total_unit']
            value_per_unit = round(total_value / total_unit, 2)
            
            # Create initial fraction with all units
            fraction = Fraction(
                asset_id=asset.asset_id,
                owner_id=owner_id,
                parent_fraction_id=None,
                units=total_unit,
                is_active=True,
                created_at=datetime.utcnow(),
                value_perunit=value_per_unit  # Store as decimal (NUMERIC(18,2))
            )
            
            db.session.add(fraction)
            
            # Create initial value history record
            value_history = AssetValueHistory(
                asset_id=asset.asset_id,
                value=total_value,
                recorded_at=datetime.utcnow(),
                source='initial_creation',
                adjusted_by=admin_user_id,  # Admin who created the asset
                adjustment_reason='Initial value'
            )
            
            db.session.add(value_history)
            db.session.commit()
            
            return {
                'asset': asset,
                'fraction': fraction,
                'value_history': value_history
            }
            
        except Exception as e:
            # Rollback asset creation if fraction or history creation fails
            db.session.rollback()
            raise ValueError(f"Failed to create initial fraction or value history: {str(e)}") from e