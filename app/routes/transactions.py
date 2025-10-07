"""
Transaction routes Blueprint for transaction management.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.transaction_controller import TransactionController

# Create Blueprint instance
bp = Blueprint('transactions', __name__, url_prefix='/transactions')

# Initialize controller
transaction_controller = TransactionController()


@bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """
    Get transaction by ID.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        JSON response with transaction data
    """
    return transaction_controller.get_transaction(transaction_id)


@bp.route('', methods=['GET'])
def get_all_transactions():
    """
    Get all transactions with pagination.
    
    Query params:
        - page: int (default 1)
        - per_page: int (default 20)
    
    Returns:
        JSON response with transactions list
    """
    return transaction_controller.get_all_transactions()


@bp.route('/fraction/<int:fraction_id>', methods=['GET'])
def get_transactions_by_fraction(fraction_id):
    """
    Get all transactions for a specific fraction.
    
    Args:
        fraction_id: Fraction ID
        
    Returns:
        JSON response with transactions list
    """
    return transaction_controller.get_transactions_by_fraction(fraction_id)


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_transactions_by_user(user_id):
    """
    Get all transactions involving a specific user.
    
    Args:
        user_id: User ID
    
    Query params:
        - transaction_type: str (optional, e.g., 'trade', 'initial')
        
    Returns:
        JSON response with transactions list
    """
    return transaction_controller.get_transactions_by_user(user_id)


@bp.route('/asset/<int:asset_id>', methods=['GET'])
def get_transactions_by_asset(asset_id):
    """
    Get all transactions for a specific asset.
    
    Args:
        asset_id: Asset ID
    
    Query params:
        - limit: int (optional)
        
    Returns:
        JSON response with transactions list
    """
    return transaction_controller.get_transactions_by_asset(asset_id)


@bp.route('/user/<int:user_id>/buy', methods=['GET'])
def get_user_buy_transactions(user_id):
    """
    Get all transactions where user was the buyer.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with buy transactions list
    """
    return transaction_controller.get_user_buy_transactions(user_id)


@bp.route('/user/<int:user_id>/sell', methods=['GET'])
def get_user_sell_transactions(user_id):
    """
    Get all transactions where user was the seller.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with sell transactions list
    """
    return transaction_controller.get_user_sell_transactions(user_id)