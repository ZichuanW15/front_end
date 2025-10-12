"""
Controller for offer filtering operations.
Handles request parsing and validation for filter endpoints.
"""

from datetime import datetime
from typing import Any, Dict, Tuple

from flask import request

from app.services.offer_filter_service import OfferFilterService
from app.views.offer_filter_view import OfferFilterView


class OfferFilterController:
    """Controller for offer filtering endpoints."""

    @staticmethod
    def filter_offers() -> Tuple[Dict[str, Any], int]:
        """
        Handle GET request for filtering offers.
        
        Query parameters:
            - asset_id: int
            - offer_type: str ('buy' or 'sell')
            - min_price: float
            - max_price: float
            - min_units: int
            - max_units: int
            - user_id: int
            - is_valid: bool
            - created_after: datetime (ISO format)
            - created_before: datetime (ISO format)
            - sort_by: str (default: 'created_at')
            - order: str ('asc' or 'desc', default: 'desc')
            - page: int (default: 1)
            - per_page: int (default: 20)
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Parse query parameters
            asset_id = request.args.get('asset_id', type=int)
            offer_type = request.args.get('offer_type', type=str)
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            min_units = request.args.get('min_units', type=int)
            max_units = request.args.get('max_units', type=int)
            user_id = request.args.get('user_id', type=int)
            
            # Handle is_valid (can be True, False, or None)
            is_valid_str = request.args.get('is_valid', 'true').lower()
            if is_valid_str == 'all':
                is_valid = None
            else:
                is_valid = is_valid_str == 'true'
            
            # Date filters
            created_after = None
            created_before = None
            if request.args.get('created_after'):
                created_after = datetime.fromisoformat(
                    request.args.get('created_after').replace('Z', '+00:00')
                )
            if request.args.get('created_before'):
                created_before = datetime.fromisoformat(
                    request.args.get('created_before').replace('Z', '+00:00')
                )
            
            # Sorting and pagination
            sort_by = request.args.get('sort_by', 'created_at')
            order = request.args.get('order', 'desc')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            # Validate parameters
            if offer_type and offer_type.lower() not in ['buy', 'sell']:
                return OfferFilterView.error("Invalid offer_type. Must be 'buy' or 'sell'"), 400
            
            if sort_by not in ['created_at', 'price_perunit', 'units']:
                return OfferFilterView.error("Invalid sort_by field"), 400
            
            if order not in ['asc', 'desc']:
                return OfferFilterView.error("Invalid order. Must be 'asc' or 'desc'"), 400
            
            if per_page > 100:
                return OfferFilterView.error("per_page cannot exceed 100"), 400
            
            # Call service
            result = OfferFilterService.filter_offers(
                asset_id=asset_id,
                offer_type=offer_type,
                min_price=min_price,
                max_price=max_price,
                min_units=min_units,
                max_units=max_units,
                user_id=user_id,
                is_valid=is_valid,
                created_after=created_after,
                created_before=created_before,
                sort_by=sort_by,
                order=order,
                page=page,
                per_page=per_page
            )
            
            return OfferFilterView.filter_success(result), 200
            
        except Exception as e:
            return OfferFilterView.error(f"Filter failed: {str(e)}"), 500

    @staticmethod
    def get_price_statistics() -> Tuple[Dict[str, Any], int]:
        """
        Handle GET request for price statistics.
        
        Query parameters:
            - asset_id: int (optional)
            - days: int (default: 30)
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            asset_id = request.args.get('asset_id', type=int)
            days = request.args.get('days', 30, type=int)
            
            if days < 1 or days > 365:
                return OfferFilterView.error("Days must be between 1 and 365"), 400
            
            result = OfferFilterService.get_price_statistics(
                asset_id=asset_id,
                days=days
            )
            
            return OfferFilterView.statistics_success(result), 200
            
        except Exception as e:
            return OfferFilterView.error(f"Statistics failed: {str(e)}"), 500

    @staticmethod
    def search_by_price_range() -> Tuple[Dict[str, Any], int]:
        """
        Handle GET request for price range search.
        
        Query parameters:
            - asset_id: int (required)
            - target_price: float (required)
            - tolerance: float (default: 5.0, percentage)
            - offer_type: str (optional, 'buy' or 'sell')
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            asset_id = request.args.get('asset_id', type=int)
            target_price = request.args.get('target_price', type=float)
            tolerance = request.args.get('tolerance', 5.0, type=float)
            offer_type = request.args.get('offer_type', type=str)
            
            if not asset_id:
                return OfferFilterView.error("asset_id is required"), 400
            
            if not target_price:
                return OfferFilterView.error("target_price is required"), 400
            
            if tolerance < 0 or tolerance > 50:
                return OfferFilterView.error("Tolerance must be between 0 and 50"), 400
            
            result = OfferFilterService.search_offers_by_price_range(
                asset_id=asset_id,
                target_price=target_price,
                tolerance_percentage=tolerance,
                offer_type=offer_type
            )
            
            return OfferFilterView.filter_success(result), 200
            
        except Exception as e:
            return OfferFilterView.error(f"Price range search failed: {str(e)}"), 500

    @staticmethod
    def get_best_offers(asset_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Handle GET request for best offers.
        
        Query parameters:
            - limit: int (default: 5)
        
        Args:
            asset_id: Asset ID from URL path
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            limit = request.args.get('limit', 5, type=int)
            
            if limit < 1 or limit > 50:
                return OfferFilterView.error("Limit must be between 1 and 50"), 400
            
            result = OfferFilterService.get_best_offers(
                asset_id=asset_id,
                limit=limit
            )
            
            return OfferFilterView.best_offers_success(result), 200
            
        except Exception as e:
            return OfferFilterView.error(f"Failed to get best offers: {str(e)}"), 500