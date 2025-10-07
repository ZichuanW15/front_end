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
            'transaction': self._format_transaction(transaction),
            'status': 'success'
        })
    
    def render_transactions_list(self, transactions):
        """
        Render transactions list response.
        
        Args:
            transactions: List of Transaction model instances
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'transactions': [self._format_transaction(t) for t in transactions],
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
    
    def _format_transaction(self, transaction):
        """
        Format a single transaction object.
        
        Args:
            transaction: Transaction model instance
            
        Returns:
            dict: Formatted transaction dictionary
        """
        return {
            'transaction_id': transaction.transaction_id,
            'fraction_id': transaction.fraction_id,
            'unit_moved': transaction.unit_moved,
            'transaction_type': transaction.transaction_type,
            'transaction_at': transaction.transaction_at.isoformat() if transaction.transaction_at else None,
            'from_owner_id': transaction.from_owner_id,
            'to_owner_id': transaction.to_owner_id,
            'offer_id': transaction.offer_id,
            'price_perunit': float(transaction.price_perunit) if transaction.price_perunit else None,
            'total_value': float(transaction.unit_moved * transaction.price_perunit) if transaction.price_perunit else None
        }