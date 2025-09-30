"""
Offer view for formatting offer-related responses.
"""

from flask import jsonify

class OfferView:
    """View class for offer responses."""
    
    def render_offer(self, offer):
        """
        Render single offer response.
        
        Args:
            offer: Offer model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'offer': self._format_offer(offer),
            'status': 'success'
        })
    
    def render_offer_created(self, offer):
        """
        Render offer creation response.
        
        Args:
            offer: Created Offer model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'offer': self._format_offer(offer),
            'message': 'Offer created successfully',
            'status': 'success'
        }), 201
    
    def render_offer_updated(self, offer):
        """
        Render offer update response.
        
        Args:
            offer: Updated Offer model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'offer': self._format_offer(offer),
            'message': 'Offer updated successfully',
            'status': 'success'
        })
    
    def render_offer_deleted(self):
        """
        Render offer deletion response.
        
        Returns:
            Response: JSON response
        """
        return jsonify({
            'message': 'Offer deactivated successfully',
            'status': 'success'
        })
    
    def render_offers_list(self, offers):
        """
        Render offers list response.
        
        Args:
            offers: List of Offer model instances
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'offers': [self._format_offer(offer) for offer in offers],
            'count': len(offers),
            'status': 'success'
        })
    
    def render_offers_paginated(self, pagination_result):
        """
        Render paginated offers list response.
        
        Args:
            pagination_result: Dictionary with offers and pagination info
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'offers': [self._format_offer(offer) for offer in pagination_result['offers']],
            'pagination': {
                'total': pagination_result['total'],
                'page': pagination_result['page'],
                'per_page': pagination_result['per_page'],
                'pages': pagination_result['pages']
            },
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
            'error': 'Offer Error',
            'message': error_message,
            'status_code': status_code
        }), status_code
    
    def _format_offer(self, offer):
        """
        Format a single offer object.
        
        Args:
            offer: Offer model instance
            
        Returns:
            dict: Formatted offer dictionary
        """
        return {
            'offer_id': offer.offer_id,
            'asset_id': offer.asset_id,
            'fraction_id': offer.fraction_id,
            'user_id': offer.user_id,
            'is_buyer': offer.is_buyer,
            'offer_type': 'buy' if offer.is_buyer else 'sell',
            'units': offer.units,
            'price_perunit': float(offer.price_perunit) if offer.price_perunit else None,
            'total_price': float(offer.units * offer.price_perunit) if offer.price_perunit else None,
            'is_valid': offer.is_valid,
            'created_at': offer.create_at.isoformat() if offer.create_at else None
        }