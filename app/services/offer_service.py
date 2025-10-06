"""
Offer service for offer-related business logic.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.database import db
from app.models import Offer, Fraction


class OfferService:
    """Service class for offer operations."""


    @staticmethod
    def create_offer(offer_data: Dict[str, Any]) -> Offer:
        """
        Create a new offer. Checks seller's total fraction units if is_buyer=False.
        
        Args:
            offer_data: Dictionary containing offer information
                Required: asset_id, user_id, is_buyer, units, price_perunit
        
        Returns:
            Offer: Created offer instance
        
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        required_fields = ['asset_id', 'user_id', 'is_buyer', 'units', 'price_perunit']
        for field in required_fields:
            if field not in offer_data or offer_data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        is_buyer = offer_data['is_buyer']
        
        # Check if user already has an active offer for this asset in the same direction
        # 只能有一个active的offer
        existing_offer = Offer.query.filter_by(
            user_id=offer_data['user_id'],
            asset_id=offer_data['asset_id'],
            is_buyer=is_buyer,
            is_valid=True
        ).first()
        
        if existing_offer:
            offer_type = 'buy' if is_buyer else 'sell'
            raise ValueError(f"User already has an active {offer_type} offer for this asset. Please update instead.")

        # Seller validation - check total available units across all active fractions
        if not is_buyer:
            # Calculate seller's total available units for this asset
            total_units = db.session.query(db.func.sum(Fraction.units)).filter(
                Fraction.asset_id == offer_data['asset_id'],
                Fraction.owner_id == offer_data['user_id'],
                Fraction.is_active.is_(True)
            ).scalar() or 0
            
            if total_units < offer_data['units']:
                raise ValueError(f"Seller only has {total_units} units available, cannot sell {offer_data['units']} units")
            
            # fraction_id is None for sell offers (determined during transaction)
            offer_data['fraction_id'] = None
        else:
            # Buyer should not have fraction_id
            offer_data['fraction_id'] = None

        # Create offer
        offer = Offer(
            asset_id=offer_data['asset_id'],
            fraction_id=None,  # Always None at creation
            user_id=offer_data['user_id'],
            is_buyer=is_buyer,
            units=offer_data['units'],
            price_perunit=offer_data['price_perunit'],
            create_at=datetime.utcnow(),
            is_valid=True
        )
        
        db.session.add(offer)
        db.session.commit()
        return offer

    @staticmethod
    def get_offer_by_id(offer_id: int) -> Optional[Offer]:
        """
        Get offer by ID.

        Args:
            offer_id: Offer ID

        Returns:
            Offer or None if not found
        """
        return Offer.query.get(offer_id)

    @staticmethod
    def get_all_offers(page: int = 1, per_page: int = 20, active_only: bool = True) -> Dict[str, Any]:
        """
        Get all offers with pagination.

        Args:
            page: Page number
            per_page: Items per page
            active_only: If True, only return active offers

        Returns:
            Dictionary containing offers list and pagination info
        """
        query = Offer.query
        
        if active_only:
            query = query.filter_by(is_valid=True)
        
        pagination = query.order_by(Offer.create_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'offers': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }

    @staticmethod
    def update_offer(offer_id: int, offer_data: Dict[str, Any]) -> Optional[Offer]:
        """
        Update an existing active offer.
        Only active offers can be updated.
        
        Args:
            offer_id: Offer ID
            offer_data: Dictionary with fields to update (units, price_perunit)
        
        Returns:
            Updated Offer or None if not found
        
        Raises:
            ValueError: If offer is inactive or validation fails
        """

        # 根据id update
        offer = Offer.query.get(offer_id)
        if not offer:
            return None
        
        if not offer.is_valid:
            raise ValueError("Cannot update an inactive offer")

        # Update allowed fields
        allowed_fields = ['units', 'price_perunit']
        for field in allowed_fields:
            if field in offer_data:
                setattr(offer, field, offer_data[field])

        # Seller validation: check total available units when units are modified
        if not offer.is_buyer and 'units' in offer_data:
            total_units = db.session.query(db.func.sum(Fraction.units)).filter(
                Fraction.asset_id == offer.asset_id,
                Fraction.owner_id == offer.user_id,
                Fraction.is_active.is_(True)
            ).scalar() or 0
            
            if total_units < offer_data['units']:
                raise ValueError(f"Seller only has {total_units} units available, cannot sell {offer_data['units']} units")

        db.session.commit()
        return offer

    @staticmethod
    def delete_offer(offer_id: int) -> bool:
        """
        Delete an offer.

        Args:
            offer_id: Offer ID

        Returns:
            True if deleted, False if not found
        """
        offer = Offer.query.get(offer_id)
        if not offer or not offer.is_valid:
            return {"success": False, "message": "Offer not found or already inactive"}

        offer.is_valid = False
        db.session.commit()
        return {"success": True, "message": "Offer deactivated"}

    @staticmethod
    def get_offers_by_user(user_id: int, active_only: bool = True) -> List[Offer]:
        """
        Get all offers created by a specific user.

        Args:
            user_id: User ID
            active_only: If True, only return active offers

        Returns:
            List of Offer objects
        """
        query = Offer.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_valid=True)
        
        return query.order_by(Offer.create_at.desc()).all()

    @staticmethod
    def get_offers_by_asset(asset_id: int, active_only: bool = True, is_buyer: Optional[bool] = None) -> List[Offer]:
        """
        Get all offers for a specific asset.

        Args:
            asset_id: Asset ID
            active_only: If True, only return active offers
            is_buyer: If specified, filter by buyer (True) or seller (False) offers

        Returns:
            List of Offer objects
        """
        query = Offer.query.filter_by(asset_id=asset_id)
        
        if active_only:
            query = query.filter_by(is_valid=True)
        
        if is_buyer is not None:
            query = query.filter_by(is_buyer=is_buyer)
        
        return query.order_by(Offer.price_perunit.asc() if is_buyer else Offer.price_perunit.desc()).all()
    
    
    @staticmethod
    def get_buy_offers(asset_id: int, active_only: bool = True) -> List[Offer]:
        """
        Get all buy offers for a specific asset, sorted by price descending (highest first).
        
        Args:
            asset_id: Asset ID
            active_only: If True, only return active offers
            
        Returns:
            List of buy Offer objects
        """
        return OfferService.get_offers_by_asset(asset_id, active_only, is_buyer=True)

    @staticmethod
    def get_sell_offers(asset_id: int, active_only: bool = True) -> List[Offer]:
        """
        Get all sell offers for a specific asset, sorted by price ascending (lowest first).
        
        Args:
            asset_id: Asset ID
            active_only: If True, only return active offers
            
        Returns:
            List of sell Offer objects
        """
        return OfferService.get_offers_by_asset(asset_id, active_only, is_buyer=False)