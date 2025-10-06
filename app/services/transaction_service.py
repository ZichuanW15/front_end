"""
Transaction service for transaction-related business logic.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import or_
from app.database import db
from app.models import Transaction, Fraction, User


class TransactionService:
    """Service class for transaction operations."""

    # transaction can only be created by trading Service
    
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
        return Transaction.query.filter_by(
            fraction_id=fraction_id
        ).order_by(Transaction.transaction_at.desc()).all()
    
    @staticmethod
    def get_transactions_by_user(user_id: int, transaction_type: Optional[str] = None) -> List[Transaction]:
        """
        Get all transactions involving a specific user (as buyer or seller).
        
        Args:
            user_id: User ID
            transaction_type: Optional filter by transaction type (e.g., 'trade', 'initial')
        
        Returns:
            List of Transaction objects
        """
        query = Transaction.query.filter(
            or_(
                Transaction.from_owner_id == user_id,
                Transaction.to_owner_id == user_id
            )
        )
        
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        return query.order_by(Transaction.transaction_at.desc()).all()
    
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
    def get_transactions_by_asset(asset_id: int, limit: Optional[int] = None) -> List[Transaction]:
        """
        Get all transactions for a specific asset.
        
        Args:
            asset_id: Asset ID
            limit: Optional limit on number of results
        
        Returns:
            List of Transaction objects
        """
        query = Transaction.query.join(Fraction).filter(
            Fraction.asset_id == asset_id
        ).order_by(Transaction.transaction_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_user_buy_transactions(user_id: int) -> List[Transaction]:
        """
        Get all transactions where user was the buyer (to_owner).
        
        Args:
            user_id: User ID
        
        Returns:
            List of Transaction objects
        """
        return Transaction.query.filter_by(
            to_owner_id=user_id
        ).order_by(Transaction.transaction_at.desc()).all()

    @staticmethod
    def get_user_sell_transactions(user_id: int) -> List[Transaction]:
        """
        Get all transactions where user was the seller (from_owner).
        
        Args:
            user_id: User ID
        
        Returns:
            List of Transaction objects
        """
        return Transaction.query.filter_by(
            from_owner_id=user_id
        ).order_by(Transaction.transaction_at.desc()).all()
