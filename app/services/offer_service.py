"""
Offer service for offer-related business logic.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from app.database import db
from app.models import Offer


class OfferService:
    """Service class for offer operations."""

    @staticmethod
    def create_offer(offer_data: Dict[str, Any]) -> Offer:
        """
        Create a new offer.

        Args:
            offer_data: Dictionary containing offer information

        Returns:
            Offer: Created offer instance

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['asset_id', 'user_id', 'is_buyer', 'units', 'price_perunit']
        for field in required_fields:
            if field not in offer_data or offer_data[field] is None:
                raise ValueError(f"Missing required field: {field}")

        offer = Offer(
            asset_id=offer_data['asset_id'],
            fraction_id=offer_data.get('fraction_id'),  # optional
            user_id=offer_data['user_id'],
            is_buyer=offer_data['is_buyer'],
            units=offer_data['units'],
            price_perunit = offer_data['price_perunit'], 
            create_at=datetime.utcnow()
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
    def get_all_offers(page: int = 1, per_page: int = 20) -> List[Offer]:
        """
        Get all offers with pagination.

        Args:
            page: Page number
            per_page: Items per page

        Returns:
            List of Offer objects
        """
        return Offer.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        ).items

    @staticmethod
    def update_offer(offer_id: int, offer_data: Dict[str, Any]) -> Optional[Offer]:
        """
        Update offer information.

        Args:
            offer_id: Offer ID
            offer_data: Dictionary containing updated offer information

        Returns:
            Updated Offer or None if not found
        """
        offer = Offer.query.get(offer_id)
        if not offer:
            return None

        allowed_fields = ['asset_id', 'fraction_id', 'user_id', 'is_buyer', 'units']
        for field in allowed_fields:
            if field in offer_data:
                setattr(offer, field, offer_data[field])

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
        if not offer:
            return False

        db.session.delete(offer)
        db.session.commit()
        return True

    @staticmethod
    def get_offers_by_user(user_id: int) -> List[Offer]:
        """
        Get all offers created by a specific user.

        Args:
            user_id: User ID

        Returns:
            List of Offer objects
        """
        return Offer.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_offers_by_asset(asset_id: int) -> List[Offer]:
        """
        Get all offers for a specific asset.

        Args:
            asset_id: Asset ID

        Returns:
            List of Offer objects
        """
        return Offer.query.filter_by(asset_id=asset_id).all()
