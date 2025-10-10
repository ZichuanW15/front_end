"""
View layer for offer filtering responses.
Formats filter results for API responses.
"""

from typing import Dict, Any


class OfferFilterView:
    """View class for formatting filter responses."""

    @staticmethod
    def filter_success(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format successful filter response."""
        return {
            'status': 'success',
            'message': 'Offers filtered successfully',
            'data': data
        }

    @staticmethod
    def statistics_success(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format successful statistics response."""
        return {
            'status': 'success',
            'message': 'Price statistics retrieved successfully',
            'data': data
        }

    @staticmethod
    def best_offers_success(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format successful best offers response."""
        return {
            'status': 'success',
            'message': 'Best offers retrieved successfully',
            'data': data
        }

    @staticmethod
    def error(message: str) -> Dict[str, Any]:
        """Format error response."""
        return {
            'status': 'error',
            'message': message
        }