"""
Offer routes Blueprint for offer management.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.offer_controller import OfferController

# Create Blueprint instance
bp = Blueprint('offers', __name__, url_prefix='/offers')

# Initialize controller
offer_controller = OfferController()


@bp.route('', methods=['POST'])
def create_offer():
    """
    Create a new offer.
    
    Returns:
        JSON response with created offer data
    """
    return offer_controller.create_offer()


@bp.route('/<int:offer_id>', methods=['GET'])
def get_offer(offer_id):
    """
    Get offer by ID.
    
    Args:
        offer_id: Offer ID
        
    Returns:
        JSON response with offer data
    """
    return offer_controller.get_offer(offer_id)


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_offers_by_user(user_id):
    """
    Get all offers created by a specific user.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with offers list
    """
    return offer_controller.get_offers_by_user(user_id)


@bp.route('/asset/<int:asset_id>', methods=['GET'])
def get_offers_by_asset(asset_id):
    """
    Get all offers for a specific asset.
    
    Args:
        asset_id: Asset ID
        
    Returns:
        JSON response with offers list
    """
    return offer_controller.get_offers_by_asset(asset_id)


@bp.route('/<int:offer_id>', methods=['PUT'])
def update_offer(offer_id):
    """
    Update offer information.
    
    Args:
        offer_id: Offer ID
        
    Returns:
        JSON response with updated offer data
    """
    return offer_controller.update_offer(offer_id)


@bp.route('/<int:offer_id>', methods=['DELETE'])
def delete_offer(offer_id):
    """
    Delete an offer.
    
    Args:
        offer_id: Offer ID
        
    Returns:
        JSON response with deletion status
    """
    return offer_controller.delete_offer(offer_id)
