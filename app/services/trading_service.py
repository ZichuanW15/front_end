"""
Trading service for handling manual trade execution.
Users manually accept existing offers (not automatic matching).
"""

from datetime import datetime
from typing import Dict, Any
from app import db
from app.models import Offer, Fraction, Transaction


class TradingService:
    """Service class for trading operations."""

    @staticmethod
    def execute_trade(offer_id: int, counterparty_user_id: int) -> Dict[str, Any]:
        """
        Execute a trade where a user accepts an existing offer.
        
        Flow:
        - If offer is a BUY offer: seller (counterparty) sells to the offer creator
        - If offer is a SELL offer: buyer (counterparty) buys from the offer creator
        
        Steps:
        1. Validate offer exists and is active
        2. Validate counterparty is not the offer creator
        3. If SELL offer: check seller has enough fractions
        4. Deactivate the offer
        5. Update fractions (deduct from seller, create for buyer)
        6. Create transaction records
        
        Args:
            offer_id: The offer being accepted
            counterparty_user_id: The user accepting the offer
        
        Returns:
            Dictionary with transaction details
        
        Raises:
            ValueError: If validation fails
        """
        # 1. Validate offer
        offer = Offer.query.get(offer_id)
        
        if not offer:
            raise ValueError("Offer not found")
        
        if not offer.is_valid:
            raise ValueError("Offer is not active")
        
        # 2. Validate counterparty is not the offer creator
        if offer.user_id == counterparty_user_id:
            raise ValueError("Cannot trade with yourself")
        
        # Determine buyer and seller based on offer type
        if offer.is_buyer:
            buyer_id = offer.user_id
            seller_id = counterparty_user_id
        else:
            buyer_id = counterparty_user_id
            seller_id = offer.user_id
        
        # 3. Get seller's fractions (oldest first, active only)
        seller_fractions = Fraction.query.filter_by(
            asset_id=offer.asset_id,
            owner_id=seller_id,
            is_active=True
        ).order_by(Fraction.created_at.asc()).all()
        
        total_available = sum(f.units for f in seller_fractions)
        
        if total_available < offer.units:
            raise ValueError(
                f"Seller only has {total_available} units available, "
                f"cannot sell {offer.units} units"
            )
        
        # Start database transaction
        try:
            # 4. Deactivate the offer
            offer.is_valid = False
            
            # 5 & 6. Process fractions and create transactions
            return TradingService._process_fractions_and_transactions(
                offer, buyer_id, seller_id, seller_fractions
            )
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Trade execution failed: {str(e)}") from e

    @staticmethod
    def _process_fractions_and_transactions(offer, buyer_id, seller_id, seller_fractions):
        """Process fractions and create transactions for a trade."""
        remaining_units = offer.units
        transactions_created = []
        
        for seller_fraction in seller_fractions:
            if remaining_units <= 0:
                break
            
            # Determine how many units to take from this fraction
            units_from_this_fraction = min(remaining_units, seller_fraction.units)
            
            # Deduct from seller's fraction
            seller_fraction.units -= units_from_this_fraction
            
            # If fraction is depleted, mark as inactive
            if seller_fraction.units == 0:
                seller_fraction.is_active = False
            
            # Create new fraction for buyer
            new_buyer_fraction = Fraction(
                asset_id=offer.asset_id,
                owner_id=buyer_id,
                parent_fraction_id=seller_fraction.fraction_id,
                units=units_from_this_fraction,
                is_active=True,
                created_at=datetime.utcnow(),
                value_perunit=offer.price_perunit
            )
            db.session.add(new_buyer_fraction)
            db.session.flush()  # Get the new fraction_id
            
            # Create transaction record
            transaction = Transaction(
                fraction_id=new_buyer_fraction.fraction_id,
                unit_moved=units_from_this_fraction,
                transaction_type='trade',
                transaction_at=datetime.utcnow(),
                from_owner_id=seller_id,
                to_owner_id=buyer_id,
                offer_id=offer.offer_id,
                price_perunit=offer.price_perunit
            )
            db.session.add(transaction)
            transactions_created.append({
                'units': units_from_this_fraction,
                'price': float(offer.price_perunit)
            })
            
            remaining_units -= units_from_this_fraction
        
        # Commit all changes
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Trade executed successfully',
            'trade_details': {
                'offer_id': offer.offer_id,
                'offer_type': 'buy' if offer.is_buyer else 'sell',
                'asset_id': offer.asset_id,
                'buyer_id': buyer_id,
                'seller_id': seller_id,
                'units_traded': offer.units,
                'price_perunit': float(offer.price_perunit),
                'total_value': float(offer.units * offer.price_perunit),
                'transactions_count': len(transactions_created)
            }
        }

    @staticmethod
    def get_asset_offers(asset_id: int) -> Dict[str, Any]:
        """
        Get all active offers for an asset, separated by buy and sell.
        
        Args:
            asset_id: Asset ID
        
        Returns:
            Dictionary with buy_offers and sell_offers lists
        """
        # Get active buy offers (highest price first)
        buy_offers = Offer.query.filter_by(
            asset_id=asset_id,
            is_buyer=True,
            is_valid=True
        ).order_by(Offer.price_perunit.desc()).all()
        
        # Get active sell offers (lowest price first)
        sell_offers = Offer.query.filter_by(
            asset_id=asset_id,
            is_buyer=False,
            is_valid=True
        ).order_by(Offer.price_perunit.asc()).all()
        
        return {
            'asset_id': asset_id,
            'buy_offers': [
                {
                    'offer_id': offer.offer_id,
                    'user_id': offer.user_id,
                    'units': offer.units,
                    'price_perunit': float(offer.price_perunit),
                    'total_value': float(offer.units * offer.price_perunit),
                    'created_at': offer.create_at.isoformat() if offer.create_at else None
                }
                for offer in buy_offers
            ],
            'sell_offers': [
                {
                    'offer_id': offer.offer_id,
                    'user_id': offer.user_id,
                    'units': offer.units,
                    'price_perunit': float(offer.price_perunit),
                    'total_value': float(offer.units * offer.price_perunit),
                    'created_at': offer.create_at.isoformat() if offer.create_at else None
                }
                for offer in sell_offers
            ],
            'buy_count': len(buy_offers),
            'sell_count': len(sell_offers)
        }