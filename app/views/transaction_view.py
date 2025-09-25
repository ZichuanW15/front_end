"""
Transaction view for formatting transaction-related responses.
"""

from flask import jsonify


class TransactionView:
    """View class for transaction responses."""
    
    def render_transaction(self, transaction):
        """
        Render single transaction response.
        
        Args:
            transaction: Transaction model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'transaction': transaction.to_dict(),
            'status': 'success'
        })
    
    def render_transaction_created(self, transaction):
        """
        Render transaction creation response.
        
        Args:
            transaction: Created Transaction model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'transaction': transaction.to_dict(),
            'message': 'Transaction created successfully',
            'status': 'success'
        }), 201
    
    def render_transactions_list(self, transactions):
        """
        Render transactions list response.
        
        Args:
            transactions: List of Transaction model instances
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in transactions],
            'count': len(transactions),
            'status': 'success'
        })
    
    def render_transaction_history(self, transactions):
        """
        Render transaction history response.
        
        Args:
            transactions: List of Transaction model instances ordered by date
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'transaction_history': [transaction.to_dict() for transaction in transactions],
            'count': len(transactions),
            'status': 'success'
        })
    
    def render_error(self, error_message, status_code):
        """
        Render error response.
        
        Args:
            error_message: Error message
            status_code: HTTP status code
            
        Returns:
            Response: JSON error response
        """
        return jsonify({
            'error': 'Transaction Error',
            'message': error_message,
            'status_code': status_code
        }), status_code