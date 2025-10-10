"""
Routes for offer filtering and search endpoints.
Place this file in: app/routes/offer_filters.py
"""

from flask import Blueprint
from app.controllers.offer_filter_controller import OfferFilterController

bp = Blueprint('offer_filters', __name__, url_prefix='/api/offers')


@bp.route('/filter', methods=['GET'])
def filter_offers():
    """
    Filter offers with multiple criteria.
    
    Query Parameters:
        - asset_id (int): Filter by specific asset
        - offer_type (str): 'buy' or 'sell'
        - min_price (float): Minimum price per unit
        - max_price (float): Maximum price per unit
        - min_units (int): Minimum units
        - max_units (int): Maximum units
        - user_id (int): Filter by offer creator
        - is_valid (str): 'true', 'false', or 'all' (default: 'true')
        - created_after (str): ISO datetime
        - created_before (str): ISO datetime
        - sort_by (str): 'created_at', 'price_perunit', 'units' (default: 'created_at')
        - order (str): 'asc' or 'desc' (default: 'desc')
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20, max: 100)
    
    Example:
        GET /api/offers/filter?asset_id=5&offer_type=sell&min_price=90&max_price=110&page=1&per_page=20
    
    Response:
        {
            "status": "success",
            "message": "Offers filtered successfully",
            "data": {
                "offers": [...],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "per_page": 20,
                    "total_pages": 5,
                    "has_next": true,
                    "has_prev": false
                },
                "filters_applied": {...}
            }
        }
    """
    return OfferFilterController.filter_offers()


@bp.route('/statistics', methods=['GET'])
def get_price_statistics():
    """
    Get price statistics for offers.
    
    Query Parameters:
        - asset_id (int): Optional, filter by specific asset
        - days (int): Number of days to look back (default: 30, max: 365)
    
    Example:
        GET /api/offers/statistics?asset_id=5&days=30
    
    Response:
        {
            "status": "success",
            "message": "Price statistics retrieved successfully",
            "data": {
                "asset_id": 5,
                "period_days": 30,
                "all_offers": {
                    "count": 50,
                    "avg_price": 100.5,
                    "min_price": 90,
                    "max_price": 110
                },
                "buy_offers": {
                    "count": 25,
                    "avg_price": 98,
                    "highest_bid": 105
                },
                "sell_offers": {
                    "count": 25,
                    "avg_price": 103,
                    "lowest_ask": 95
                },
                "spread": {
                    "value": -10,
                    "percentage": -9.52
                }
            }
        }
    """
    return OfferFilterController.get_price_statistics()


@bp.route('/search/price-range', methods=['GET'])
def search_by_price_range():
    """
    Search offers within a price range around a target price.
    
    Query Parameters:
        - asset_id (int): Required, asset to search
        - target_price (float): Required, target price per unit
        - tolerance (float): Percentage tolerance (default: 5.0, max: 50)
        - offer_type (str): Optional, 'buy' or 'sell'
    
    Example:
        GET /api/offers/search/price-range?asset_id=5&target_price=100&tolerance=5
        
        Returns offers between $95 and $105
    
    Response:
        Same as /filter endpoint
    """
    return OfferFilterController.search_by_price_range()


@bp.route('/best/<int:asset_id>', methods=['GET'])
def get_best_offers(asset_id):
    """
    Get best buy and sell offers for an asset.
    
    Best buy offers = highest prices (buyers willing to pay most)
    Best sell offers = lowest prices (sellers asking least)
    
    Path Parameters:
        - asset_id (int): Asset ID
    
    Query Parameters:
        - limit (int): Number of offers per side (default: 5, max: 50)
    
    Example:
        GET /api/offers/best/5?limit=10
    
    Response:
        {
            "status": "success",
            "message": "Best offers retrieved successfully",
            "data": {
                "asset_id": 5,
                "best_buy_offers": [
                    {
                        "offer_id": 123,
                        "user_id": 1,
                        "units": 10,
                        "price_perunit": 105.0,
                        "total_value": 1050.0
                    }
                ],
                "best_sell_offers": [
                    {
                        "offer_id": 124,
                        "user_id": 2,
                        "units": 15,
                        "price_perunit": 95.0,
                        "total_value": 1425.0
                    }
                ],
                "spread": {
                    "bid": 105.0,
                    "ask": 95.0,
                    "spread": -10.0
                }
            }
        }
    """
    return OfferFilterController.get_best_offers(asset_id)