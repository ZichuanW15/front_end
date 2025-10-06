"""
Offer controller for offer management.
Handles business logic and communicates with the OfferService and OfferView.
"""

from flask import request
from app.services.offer_service import OfferService
from app.views.offer_view import OfferView
from app.controllers.base_controller import BaseController


class OfferController(BaseController):
    """Controller for handling offer routes."""

    def __init__(self):
        self.service = OfferService()
        self.view = OfferView()

    def create_offer(self):
        """Create a new offer."""
        def _create():
            data = request.json
            offer = self.service.create_offer(data)
            return self.view.render_offer_created(offer)
        return self.handle_request(_create)

    def get_offer(self, offer_id: int):
        """Get offer by ID."""
        offer = self.service.get_offer_by_id(offer_id)
        if not offer:
            return self.view.render_error(f"Offer {offer_id} not found", 404)
        return self.view.render_offer(offer)

    def get_all_offers(self):
        """Get all offers with pagination."""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            active_only = request.args.get('active_only', 'true').lower() == 'true'
            
            result = self.service.get_all_offers(page, per_page, active_only)
            return self.view.render_offers_paginated(result)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)

    def get_offers_by_user(self, user_id: int):
        """Get all offers created by a specific user."""
        try:
            active_only = request.args.get('active_only', 'true').lower() == 'true'
            offers = self.service.get_offers_by_user(user_id, active_only)
            return self.view.render_offers_list(offers)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)

    def get_offers_by_asset(self, asset_id: int):
        """Get all offers for a specific asset."""
        try:
            active_only = request.args.get('active_only', 'true').lower() == 'true'
            is_buyer_str = request.args.get('is_buyer')
            is_buyer = None
            if is_buyer_str is not None:
                is_buyer = is_buyer_str.lower() == 'true'
            
            offers = self.service.get_offers_by_asset(asset_id, active_only, is_buyer)
            return self.view.render_offers_list(offers)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)

    def get_buy_offers(self, asset_id: int):
        """Get all buy offers for a specific asset."""
        try:
            active_only = request.args.get('active_only', 'true').lower() == 'true'
            offers = self.service.get_buy_offers(asset_id, active_only)
            return self.view.render_offers_list(offers)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)

    def get_sell_offers(self, asset_id: int):
        """Get all sell offers for a specific asset."""
        try:
            active_only = request.args.get('active_only', 'true').lower() == 'true'
            offers = self.service.get_sell_offers(asset_id, active_only)
            return self.view.render_offers_list(offers)
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)

    def update_offer(self, offer_id: int):
        """Update an existing offer."""
        def _update():
            data = request.json
            offer = self.service.update_offer(offer_id, data)
            if not offer:
                return self.view.render_error(f"Offer {offer_id} not found", 404)
            return self.view.render_offer_updated(offer)
        return self.handle_request(_update)

    def delete_offer(self, offer_id: int):
        """Delete an offer."""
        try:
            success = self.service.delete_offer(offer_id)
            if not success:
                return self.view.render_error(f"Offer {offer_id} not found or already inactive", 404)
            return self.view.render_offer_deleted()
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)