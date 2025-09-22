"""
Transaction controller for handling transaction-related requests.
"""

from flask import request
from app.services.transaction_service import TransactionService
from app.views.transaction_view import TransactionView


class TransactionController:
    """Controller for transaction operations."""
    
    def __init__(self):
        self.transaction_service = TransactionService()
        self.transaction_view = TransactionView()
    
    def create_transaction(self):
        """
        Handle transaction creation request.
        
        Returns:
            Response: JSON response with created transaction data
        """
        try:
            transaction_data = request.get_json()
            if not transaction_data:
                return self.transaction_view.render_error("No JSON data provided", 400)
            
            transaction = self.transaction_service.create_transaction(transaction_data)
            return self.transaction_view.render_transaction_created(transaction)
        except ValueError as e:
            return self.transaction_view.render_error(str(e), 400)
        except Exception as e:
            return self.transaction_view.render_error(str(e), 500)
    
    def get_transaction(self, transaction_id):
        """
        Handle get transaction by ID request.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Response: JSON response with transaction data
        """
        try:
            transaction = self.transaction_service.get_transaction_by_id(transaction_id)
            if not transaction:
                return self.transaction_view.render_error("Transaction not found", 404)
            
            return self.transaction_view.render_transaction(transaction)
        except Exception as e:
            return self.transaction_view.render_error(str(e), 500)
    
    def get_transactions_by_fraction(self, fraction_id):
        """
        Handle get transactions by fraction request.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            Response: JSON response with transactions list
        """
        try:
            transactions = self.transaction_service.get_transactions_by_fraction(fraction_id)
            return self.transaction_view.render_transactions_list(transactions)
        except Exception as e:
            return self.transaction_view.render_error(str(e), 500)
    
    def get_transactions_by_user(self, user_id):
        """
        Handle get transactions by user request.
        
        Args:
            user_id: User ID
            
        Returns:
            Response: JSON response with transactions list
        """
        try:
            transactions = self.transaction_service.get_transactions_by_user(user_id)
            return self.transaction_view.render_transactions_list(transactions)
        except Exception as e:
            return self.transaction_view.render_error(str(e), 500)
    
    def get_all_transactions(self):
        """
        Handle get all transactions request.
        
        Returns:
            Response: JSON response with transactions list
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            transactions = self.transaction_service.get_all_transactions(page, per_page)
            return self.transaction_view.render_transactions_list(transactions)
        except Exception as e:
            return self.transaction_view.render_error(str(e), 500)
    
    def get_transaction_history(self, fraction_id):
        """
        Handle get transaction history request.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            Response: JSON response with transaction history
        """
        try:
            transactions = self.transaction_service.get_transaction_history(fraction_id)
            return self.transaction_view.render_transaction_history(transactions)
        except Exception as e:
            return self.transaction_view.render_error(str(e), 500)