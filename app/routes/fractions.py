"""
Fraction routes Blueprint for fraction management.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.fraction_controller import FractionController

# Create Blueprint instance
bp = Blueprint('fractions', __name__, url_prefix='/fractions')

# Initialize controller
fraction_controller = FractionController()


@bp.route('', methods=['POST'])
def create_fraction():
    """
    Create a new fraction.
    
    Returns:
        JSON response with created fraction data
    """
    return fraction_controller.create_fraction()


@bp.route('/<int:fraction_id>', methods=['GET'])
def get_fraction(fraction_id):
    """
    Get fraction by ID.
    
    Args:
        fraction_id: Fraction ID
        
    Returns:
        JSON response with fraction data
    """
    return fraction_controller.get_fraction(fraction_id)


@bp.route('/owner/<int:owner_id>', methods=['GET'])
def get_fractions_by_owner(owner_id):
    """
    Get all fractions owned by a user.
    
    Args:
        owner_id: Owner user ID
        
    Returns:
        JSON response with fractions list
    """
    return fraction_controller.get_fractions_by_owner(owner_id)


@bp.route('/asset/<int:asset_id>', methods=['GET'])
def get_fractions_by_asset(asset_id):
    """
    Get all fractions for an asset.
    
    Args:
        asset_id: Asset ID
        
    Returns:
        JSON response with fractions list
    """
    return fraction_controller.get_fractions_by_asset(asset_id)


@bp.route('/active', methods=['GET'])
def get_active_fractions():
    """
    Get all active fractions.
    
    Returns:
        JSON response with active fractions list
    """
    return fraction_controller.get_active_fractions()


@bp.route('/<int:fraction_id>', methods=['PUT'])
def update_fraction(fraction_id):
    """
    Update fraction information.
    
    Args:
        fraction_id: Fraction ID
        
    Returns:
        JSON response with updated fraction data
    """
    return fraction_controller.update_fraction(fraction_id)


@bp.route('/<int:fraction_id>', methods=['DELETE'])
def delete_fraction(fraction_id):
    """
    Delete a fraction.
    
    Args:
        fraction_id: Fraction ID
        
    Returns:
        JSON response with deletion status
    """
    return fraction_controller.delete_fraction(fraction_id)