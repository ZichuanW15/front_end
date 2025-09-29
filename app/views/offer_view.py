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
            'offer': offer.to_dict(),
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
            'offer': offer.to_dict(),
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
            'offer': offer.to_dict(),
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
            'message': 'Offer deleted successfully',
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
            'offers': [offer.to_dict() for offer in offers],
            'count': len(offers),
            'status': 'success'
        })

    def render_error(self, error_message, status_code=400):
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
