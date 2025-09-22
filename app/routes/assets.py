"""
Asset routes Blueprint for asset management.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.asset_controller import AssetController

# Create Blueprint instance
bp = Blueprint('assets', __name__, url_prefix='/api/assets')

# Initialize controller
asset_controller = AssetController()


@bp.route('', methods=['POST'])
def create_asset():
    """
    Create a new asset.
    
    Returns:
        JSON response with created asset data
    """
    return asset_controller.create_asset()


@bp.route('/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    """
    Get asset by ID.
    
    Args:
        asset_id: Asset ID
        
    Returns:
        JSON response with asset data
    """
    return asset_controller.get_asset(asset_id)


@bp.route('', methods=['GET'])
def get_assets():
    """
    Get all assets with pagination.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        
    Returns:
        JSON response with assets list
    """
    return asset_controller.get_assets()


@bp.route('/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """
    Update asset information.
    
    Args:
        asset_id: Asset ID
        
    Returns:
        JSON response with updated asset data
    """
    return asset_controller.update_asset(asset_id)


@bp.route('/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """
    Delete an asset.
    
    Args:
        asset_id: Asset ID
        
    Returns:
        JSON response with deletion status
    """
    return asset_controller.delete_asset(asset_id)


@bp.route('/<int:asset_id>/fractions', methods=['GET'])
def get_asset_fractions(asset_id):
    """
    Get all fractions for an asset.
    
    Args:
        asset_id: Asset ID
        
    Returns:
        JSON response with fractions list
    """
    return asset_controller.get_asset_fractions(asset_id)