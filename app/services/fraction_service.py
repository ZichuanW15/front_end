"""
Fraction service for fraction-related business logic.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.database import db
from app.models import Fraction, Asset, User


class FractionService:
    """Service class for fraction operations."""
    
    @staticmethod
    def create_fraction(fraction_data: Dict[str, Any]) -> Fraction:
        """
        Create a new fraction.
        
        Args:
            fraction_data: Dictionary containing fraction information
            
        Returns:
            Fraction: Created fraction instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ['asset_id', 'units']
        for field in required_fields:
            if field not in fraction_data or fraction_data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate asset exists
        asset = Asset.query.get(fraction_data['asset_id'])
        if not asset:
            raise ValueError("Asset not found")
        
        # Validate units are within asset limits
        units = fraction_data['units']
        if units < asset.unit_min or units > asset.unit_max:
            raise ValueError(f"Units must be between {asset.unit_min} and {asset.unit_max}")
        
        fraction = Fraction(
            asset_id=fraction_data['asset_id'],
            owner_id=fraction_data.get('owner_id'),
            parent_fraction_id=fraction_data.get('parent_fraction_id'),
            units=units,
            is_active=fraction_data.get('is_active', True),
            created_at=datetime.utcnow(),
            value_perunit=fraction_data.get('value_perunit')
        )
        
        db.session.add(fraction)
        db.session.commit()
        return fraction
    
    @staticmethod
    def get_fraction_by_id(fraction_id: int) -> Optional[Fraction]:
        """
        Get fraction by ID.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            Fraction or None if not found
        """
        return Fraction.query.get(fraction_id)
    
    @staticmethod
    def get_fractions_by_owner(owner_id: int) -> List[Fraction]:
        """
        Get all fractions owned by a user.
        
        Args:
            owner_id: Owner user ID
            
        Returns:
            List of Fraction objects
        """
        return Fraction.query.filter_by(owner_id=owner_id).all()
    
    @staticmethod
    def get_fractions_by_asset(asset_id: int) -> List[Fraction]:
        """
        Get all fractions for an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            List of Fraction objects
        """
        return Fraction.query.filter_by(asset_id=asset_id).all()
    
    @staticmethod
    def update_fraction(fraction_id: int, fraction_data: Dict[str, Any]) -> Optional[Fraction]:
        """
        Update fraction information.
        
        Args:
            fraction_id: Fraction ID
            fraction_data: Dictionary containing updated fraction information
            
        Returns:
            Updated Fraction or None if not found
        """
        fraction = Fraction.query.get(fraction_id)
        if not fraction:
            return None
        
        # Update allowed fields
        allowed_fields = ['owner_id', 'units', 'is_active', 'value_perunit']
        for field in allowed_fields:
            if field in fraction_data:
                setattr(fraction, field, fraction_data[field])
        
        db.session.commit()
        return fraction
    
    @staticmethod
    def delete_fraction(fraction_id: int) -> bool:
        """
        Delete a fraction.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            True if deleted, False if not found
        """
        fraction = Fraction.query.get(fraction_id)
        if not fraction:
            return False
        
        db.session.delete(fraction)
        db.session.commit()
        return True
    
    @staticmethod
    def get_active_fractions() -> List[Fraction]:
        """
        Get all active fractions.
        
        Returns:
            List of active Fraction objects
        """
        return Fraction.query.filter_by(is_active=True).all()