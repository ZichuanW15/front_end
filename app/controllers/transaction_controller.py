"""
Transaction controller for handling transaction-related requests.
"""

from flask import request
from app.services.transaction_service import TransactionService
from app.views.transaction_view import TransactionView

class TransactionController:
    """Controller for transaction operations."""
    
    def __init__(self):
        self.service = TransactionService()
        self.view = TransactionView()
    
    def get_transaction(self, transaction_id):
        """
        Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Response: JSON response with transaction data
        """
        try:
            transaction = self.service.get_transaction_by_id(transaction_id)
            if not transaction:
                return self.view.render_error(f"Transaction {transaction_id} not found", 404)
            
            return self.view.render_transaction(transaction)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)
    
    def get_all_transactions(self):
        """
        Get all transactions with pagination.
        
        Query Parameters:
            page: Page number (default: 1)
            per_page: Items per page (default: 20)
        
        Returns:
            Response: JSON response with transactions list
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            transactions = self.service.get_all_transactions(page, per_page)
            return self.view.render_transactions_list(transactions)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)
    
    def get_transactions_by_fraction(self, fraction_id):
        """
        Get all transactions for a specific fraction.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            Response: JSON response with transactions list
        """
        try:
            transactions = self.service.get_transactions_by_fraction(fraction_id)
            return self.view.render_transactions_list(transactions)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)
    
    def get_transactions_by_user(self, user_id):
        """
        Get all transactions involving a specific user.
        
        Args:
            user_id: User ID
        
        Query Parameters:
            transaction_type: Optional filter by type (e.g., 'trade', 'initial')
            
        Returns:
            Response: JSON response with transactions list
        """
        try:
            transaction_type = request.args.get('transaction_type')
            transactions = self.service.get_transactions_by_user(user_id, transaction_type)
            return self.view.render_transactions_list(transactions)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)
    
    def get_transactions_by_asset(self, asset_id):
        """
        Get all transactions for a specific asset.
        
        Args:
            asset_id: Asset ID
        
        Query Parameters:
            limit: Optional limit on number of results
            
        Returns:
            Response: JSON response with transactions list
        """
        try:
            limit = request.args.get('limit', type=int)
            transactions = self.service.get_transactions_by_asset(asset_id, limit)
            return self.view.render_transactions_list(transactions)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)
    
    def get_user_buy_transactions(self, user_id):
        """
        Get all transactions where user was the buyer.
        
        Args:
            user_id: User ID
            
        Returns:
            Response: JSON response with buy transactions list
        """
        try:
            transactions = self.service.get_user_buy_transactions(user_id)
            return self.view.render_transactions_list(transactions)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)
    
    def get_user_sell_transactions(self, user_id):
        """
        Get all transactions where user was the seller.
        
        Args:
            user_id: User ID
            
        Returns:
            Response: JSON response with sell transactions list
        """
        try:
            transactions = self.service.get_user_sell_transactions(user_id)
            return self.view.render_transactions_list(transactions)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)