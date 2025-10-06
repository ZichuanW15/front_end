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
    
    Request body:
    {
        "asset_id": 1,
        "user_id": 1,
        "is_buyer": true/false,
        "units": 100,
        "price_perunit": 50.00
    }
    
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


@bp.route('', methods=['GET'])
def get_all_offers():
    """
    Get all offers with pagination.
    
    Query params:
        - page: int (default 1)
        - per_page: int (default 20)
        - active_only: bool (default true)
    
    Returns:
        JSON response with paginated offers list
    """
    return offer_controller.get_all_offers()


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_offers_by_user(user_id):
    """
    Get all offers created by a specific user.
    
    Args:
        user_id: User ID
    
    Query params:
        - active_only: bool (default true)
        
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
    
    Query params:
        - active_only: bool (default true)
        - is_buyer: bool (optional, filter by buyer/seller)
        
    Returns:
        JSON response with offers list
    """
    return offer_controller.get_offers_by_asset(asset_id)


@bp.route('/asset/<int:asset_id>/buy', methods=['GET'])
def get_buy_offers(asset_id):
    """
    Get all buy offers for a specific asset (sorted by price descending).
    
    Args:
        asset_id: Asset ID
    
    Query params:
        - active_only: bool (default true)
        
    Returns:
        JSON response with buy offers list
    """
    return offer_controller.get_buy_offers(asset_id)


@bp.route('/asset/<int:asset_id>/sell', methods=['GET'])
def get_sell_offers(asset_id):
    """
    Get all sell offers for a specific asset (sorted by price ascending).
    
    Args:
        asset_id: Asset ID
    
    Query params:
        - active_only: bool (default true)
        
    Returns:
        JSON response with sell offers list
    """
    return offer_controller.get_sell_offers(asset_id)


@bp.route('/<int:offer_id>', methods=['PUT'])
def update_offer(offer_id):
    """
    Update offer information.
    
    Args:
        offer_id: Offer ID
    
    Request body:
    {
        "units": 150,
        "price_perunit": 55.00
    }
        
    Returns:
        JSON response with updated offer data
    """
    return offer_controller.update_offer(offer_id)


@bp.route('/<int:offer_id>', methods=['DELETE'])
def delete_offer(offer_id):
    """
    Delete (deactivate) an offer.
    
    Args:
        offer_id: Offer ID
        
    Returns:
        JSON response with deletion status
    """
    return offer_controller.delete_offer(offer_id)