"""
Transaction routes Blueprint for transaction management.
Uses MVC architecture with controllers and views.
"""

from flask import Blueprint
from app.controllers.transaction_controller import TransactionController

# Create Blueprint instance
bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# Initialize controller
transaction_controller = TransactionController()


@bp.route('', methods=['POST'])
def create_transaction():
    """
    Create a new transaction.
    
    Returns:
        JSON response with created transaction data
    """
    return transaction_controller.create_transaction()


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
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        
    Returns:
        JSON response with transactions list
    """
    return transaction_controller.get_all_transactions()


@bp.route('/fraction/<int:fraction_id>', methods=['GET'])
def get_transactions_by_fraction(fraction_id):
    """
    Get all transactions for a fraction.
    
    Args:
        fraction_id: Fraction ID
        
    Returns:
        JSON response with transactions list
    """
    return transaction_controller.get_transactions_by_fraction(fraction_id)


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_transactions_by_user(user_id):
    """
    Get all transactions involving a user.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with transactions list
    """
    return transaction_controller.get_transactions_by_user(user_id)


@bp.route('/fraction/<int:fraction_id>/history', methods=['GET'])
def get_transaction_history(fraction_id):
    """
    Get transaction history for a fraction.
    
    Args:
        fraction_id: Fraction ID
        
    Returns:
        JSON response with transaction history
    """
    return transaction_controller.get_transaction_history(fraction_id)