"""
Offer filtering service for advanced search and filtering.
Provides flexible filtering options for offers with price, units, and user filters.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, or_

from app import db
from app.models import Offer, Asset, User

class OfferFilterService:
    """Service class for filtering and searching offers."""

    @staticmethod
    def filter_offers(
        asset_id: Optional[int] = None,
        offer_type: Optional[str] = None,  # 'buy' or 'sell'
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_units: Optional[int] = None,
        max_units: Optional[int] = None,
        user_id: Optional[int] = None,  # Filter by offer creator
        is_valid: Optional[bool] = True,  # Only active offers by default
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        sort_by: str = 'created_at',  # created_at, price_perunit, units
        order: str = 'desc',  # asc or desc
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Filter offers with multiple criteria.
        
        Args:
            asset_id: Filter by specific asset
            offer_type: 'buy' or 'sell'
            min_price: Minimum price per unit
            max_price: Maximum price per unit
            min_units: Minimum units
            max_units: Maximum units
            user_id: Filter by offer creator
            is_valid: Filter by offer validity (True=active, False=inactive, None=all)
            created_after: Offers created after this date
            created_before: Offers created before this date
            sort_by: Field to sort by
            order: Sort order (asc/desc)
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            Dictionary with filtered offers and pagination info
        """
        # Build query
        query = Offer.query
        
        # Apply filters
        filters = []
        
        if asset_id is not None:
            filters.append(Offer.asset_id == asset_id)
        
        if offer_type is not None:
            if offer_type.lower() == 'buy':
                filters.append(Offer.is_buyer == True)
            elif offer_type.lower() == 'sell':
                filters.append(Offer.is_buyer == False)
        
        if min_price is not None:
            filters.append(Offer.price_perunit >= min_price)
        
        if max_price is not None:
            filters.append(Offer.price_perunit <= max_price)
        
        if min_units is not None:
            filters.append(Offer.units >= min_units)
        
        if max_units is not None:
            filters.append(Offer.units <= max_units)
        
        if user_id is not None:
            filters.append(Offer.user_id == user_id)
        
        if is_valid is not None:
            filters.append(Offer.is_valid == is_valid)
        
        if created_after is not None:
            filters.append(Offer.create_at >= created_after)
        
        if created_before is not None:
            filters.append(Offer.create_at <= created_before)
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Apply sorting
        sort_field = getattr(Offer, sort_by, Offer.create_at)
        if order.lower() == 'desc':
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Format results
        offers = []
        for offer in pagination.items:
            # Get asset info
            asset = Asset.query.get(offer.asset_id)
            # Get user info
            user = User.query.get(offer.user_id)
            
            offers.append({
                'offer_id': offer.offer_id,
                'user_id': offer.user_id,
                'user_name': user.user_name if user else None,
                'asset_id': offer.asset_id,
                'asset_name': asset.asset_name if asset else None,
                'offer_type': 'buy' if offer.is_buyer else 'sell',
                'units': offer.units,
                'price_perunit': float(offer.price_perunit),
                'total_value': float(offer.units * offer.price_perunit),
                'is_valid': offer.is_valid,
                'created_at': offer.create_at.isoformat() if offer.create_at else None
            })
        
        return {
            'offers': offers,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters_applied': {
                'asset_id': asset_id,
                'offer_type': offer_type,
                'price_range': {
                    'min': min_price,
                    'max': max_price
                },
                'units_range': {
                    'min': min_units,
                    'max': max_units
                },
                'user_id': user_id,
                'is_valid': is_valid
            }
        }

    @staticmethod
    def get_price_statistics(
        asset_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get price statistics for offers.
        
        Args:
            asset_id: Optional asset ID to filter by
            days: Number of days to look back
            
        Returns:
            Dictionary with price statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = Offer.query.filter(
            Offer.create_at >= cutoff_date,
            Offer.is_valid == True
        )
        
        if asset_id:
            query = query.filter(Offer.asset_id == asset_id)
        
        offers = query.all()
        
        if not offers:
            return {
                'asset_id': asset_id,
                'period_days': days,
                'data_available': False,
                'message': 'No offers found in the specified period'
            }
        
        prices = [float(offer.price_perunit) for offer in offers]
        buy_offers = [o for o in offers if o.is_buyer]
        sell_offers = [o for o in offers if not o.is_buyer]
        
        buy_prices = [float(o.price_perunit) for o in buy_offers] if buy_offers else []
        sell_prices = [float(o.price_perunit) for o in sell_offers] if sell_offers else []
        
        return {
            'asset_id': asset_id,
            'period_days': days,
            'data_available': True,
            'all_offers': {
                'count': len(offers),
                'avg_price': sum(prices) / len(prices) if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
            },
            'buy_offers': {
                'count': len(buy_offers),
                'avg_price': sum(buy_prices) / len(buy_prices) if buy_prices else 0,
                'highest_bid': max(buy_prices) if buy_prices else 0,
            },
            'sell_offers': {
                'count': len(sell_offers),
                'avg_price': sum(sell_prices) / len(sell_prices) if sell_prices else 0,
                'lowest_ask': min(sell_prices) if sell_prices else 0,
            },
            'spread': {
                'value': min(sell_prices) - max(buy_prices) if buy_prices and sell_prices else 0,
                'percentage': ((min(sell_prices) - max(buy_prices)) / max(buy_prices) * 100) 
                             if buy_prices and sell_prices else 0
            }
        }

    @staticmethod
    def search_offers_by_price_range(
        asset_id: int,
        target_price: float,
        tolerance_percentage: float = 5.0,
        offer_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search offers within a price range around a target price.
        
        Example: If target_price=100 and tolerance=5%, 
                 returns offers between $95 and $105
        
        Args:
            asset_id: Asset ID
            target_price: Target price per unit
            tolerance_percentage: Percentage tolerance (default 5%)
            offer_type: Optional 'buy' or 'sell' filter
            
        Returns:
            Dictionary with matching offers
        """
        min_price = target_price * (1 - tolerance_percentage / 100)
        max_price = target_price * (1 + tolerance_percentage / 100)
        
        return OfferFilterService.filter_offers(
            asset_id=asset_id,
            offer_type=offer_type,
            min_price=min_price,
            max_price=max_price,
            is_valid=True,
            sort_by='price_perunit',
            order='asc'
        )

    @staticmethod
    def get_best_offers(
        asset_id: int,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get best buy and sell offers for an asset.
        
        Best buy offers = highest prices (buyers willing to pay most)
        Best sell offers = lowest prices (sellers asking least)
        
        Args:
            asset_id: Asset ID
            limit: Number of offers to return for each side
            
        Returns:
            Dictionary with best buy and sell offers
        """
        # Best buy offers (highest prices first)
        best_buys = Offer.query.filter_by(
            asset_id=asset_id,
            is_buyer=True,
            is_valid=True
        ).order_by(Offer.price_perunit.desc()).limit(limit).all()
        
        # Best sell offers (lowest prices first)
        best_sells = Offer.query.filter_by(
            asset_id=asset_id,
            is_buyer=False,
            is_valid=True
        ).order_by(Offer.price_perunit.asc()).limit(limit).all()
        
        return {
            'asset_id': asset_id,
            'best_buy_offers': [
                {
                    'offer_id': offer.offer_id,
                    'user_id': offer.user_id,
                    'units': offer.units,
                    'price_perunit': float(offer.price_perunit),
                    'total_value': float(offer.units * offer.price_perunit)
                }
                for offer in best_buys
            ],
            'best_sell_offers': [
                {
                    'offer_id': offer.offer_id,
                    'user_id': offer.user_id,
                    'units': offer.units,
                    'price_perunit': float(offer.price_perunit),
                    'total_value': float(offer.units * offer.price_perunit)
                }
                for offer in best_sells
            ],
            'spread': {
                'bid': float(best_buys[0].price_perunit) if best_buys else 0,
                'ask': float(best_sells[0].price_perunit) if best_sells else 0,
                'spread': float(best_sells[0].price_perunit - best_buys[0].price_perunit) 
                         if best_buys and best_sells else 0
            }
        }