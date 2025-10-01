"""
Transaction service for transaction-related business logic.
"""

from app.database import db
from app.models import Transaction, Fraction, User
from datetime import datetime
from typing import Optional, List, Dict, Any


class TransactionService:
    """Service class for transaction operations."""
    
    @staticmethod
    def create_transaction(transaction_data: Dict[str, Any]) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            transaction_data: Dictionary containing transaction information
            
        Returns:
            Transaction: Created transaction instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ['fraction_id', 'unit_moved', 'from_owner_id', 'to_owner_id']
        for field in required_fields:
            if field not in transaction_data or transaction_data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate fraction exists
        fraction = Fraction.query.get(transaction_data['fraction_id'])
        if not fraction:
            raise ValueError("Fraction not found")
        
        # Validate users exist
        from_user = User.query.get(transaction_data['from_owner_id'])
        to_user = User.query.get(transaction_data['to_owner_id'])
        if not from_user or not to_user:
            raise ValueError("Invalid user IDs")
        
        # Validate unit_moved is positive
        unit_moved = transaction_data['unit_moved']
        if unit_moved <= 0:
            raise ValueError("Unit moved must be positive")
        
        transaction = Transaction(
            fraction_id=transaction_data['fraction_id'],
            unit_moved=unit_moved,
            transaction_type=transaction_data.get('transaction_type', 'transfer'),
            transaction_at=datetime.utcnow(),
            from_owner_id=transaction_data['from_owner_id'],
            to_owner_id=transaction_data['to_owner_id']
        )
        
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    @staticmethod
    def get_transaction_by_id(transaction_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction or None if not found
        """
        return Transaction.query.get(transaction_id)
    
    @staticmethod
    def get_transactions_by_fraction(fraction_id: int) -> List[Transaction]:
        """
        Get all transactions for a fraction.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            List of Transaction objects
        """
        return Transaction.query.filter_by(fraction_id=fraction_id).all()
    
    @staticmethod
    def get_transactions_by_user(user_id: int) -> List[Transaction]:
        """
        Get all transactions involving a user (as sender or receiver).
        
        Args:
            user_id: User ID
            
        Returns:
            List of Transaction objects
        """
        return Transaction.query.filter(
            (Transaction.from_owner_id == user_id) | 
            (Transaction.to_owner_id == user_id)
        ).all()
    
    @staticmethod
    def get_all_transactions(page: int = 1, per_page: int = 20) -> List[Transaction]:
        """
        Get all transactions with pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            List of Transaction objects
        """
        return Transaction.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        ).items
    
    @staticmethod
    def get_transaction_history(fraction_id: int) -> List[Transaction]:
        """
        Get transaction history for a fraction ordered by date.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            List of Transaction objects ordered by transaction_at
        """
        return Transaction.query.filter_by(fraction_id=fraction_id)\
                              .order_by(Transaction.transaction_at.desc()).all()