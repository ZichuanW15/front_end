"""
Offer controller for offer management.
Handles business logic and communicates with the OfferService and OfferView.
"""

from flask import request
from app.services.offer_service import OfferService
from app.views.offer_view import OfferView


class OfferController:
    """Controller for handling offer routes."""

    def __init__(self):
        self.service = OfferService()
        self.view = OfferView()

    def create_offer(self):
        """Create a new offer."""
        try:
            data = request.json
            offer = self.service.create_offer(data)
            return self.view.render_offer_created(offer)
        except ValueError as e:
            return self.view.render_error(str(e), 400)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)

    def get_offer(self, offer_id: int):
        """Get offer by ID."""
        offer = self.service.get_offer_by_id(offer_id)
        if not offer:
            return self.view.render_error(f"Offer {offer_id} not found", 404)
        return self.view.render_offer(offer)

    def get_offers_by_user(self, user_id: int):
        """Get all offers created by a specific user."""
        offers = self.service.get_offers_by_user(user_id)
        return self.view.render_offers_list(offers)

    def get_offers_by_asset(self, asset_id: int):
        """Get all offers for a specific asset."""
        offers = self.service.get_offers_by_asset(asset_id)
        return self.view.render_offers_list(offers)

    def update_offer(self, offer_id: int):
        """Update an existing offer."""
        data = request.json
        offer = self.service.update_offer(offer_id, data)
        if not offer:
            return self.view.render_error(f"Offer {offer_id} not found", 404)
        return self.view.render_offer_updated(offer)

    def delete_offer(self, offer_id: int):
        """Delete an offer."""
        success = self.service.delete_offer(offer_id)
        if not success:
            return self.view.render_error(f"Offer {offer_id} not found", 404)
        return self.view.render_offer_deleted()
