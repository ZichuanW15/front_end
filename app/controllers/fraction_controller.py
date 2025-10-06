"""
Fraction controller for handling fraction-related requests.
"""

from flask import request
from app.services.fraction_service import FractionService
from app.views.fraction_view import FractionView


class FractionController:
    """Controller for fraction operations."""
    
    def __init__(self):
        self.fraction_service = FractionService()
        self.fraction_view = FractionView()
    
    def create_fraction(self):
        """
        Handle fraction creation request.
        
        Returns:
            Response: JSON response with created fraction data
        """
        try:
            fraction_data = request.get_json()
            if not fraction_data:
                return self.fraction_view.render_error("No JSON data provided", 400)
            
            fraction = self.fraction_service.create_fraction(fraction_data)
            return self.fraction_view.render_fraction_created(fraction)
        except ValueError as e:
            return self.fraction_view.render_error(str(e), 400)
        except Exception as e:
            return self.fraction_view.render_error(str(e), 500)
    
    def get_fraction(self, fraction_id):
        """
        Handle get fraction by ID request.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            Response: JSON response with fraction data
        """
        try:
            fraction = self.fraction_service.get_fraction_by_id(fraction_id)
            if not fraction:
                return self.fraction_view.render_error("Fraction not found", 404)
            
            return self.fraction_view.render_fraction(fraction)
        except Exception as e:
            return self.fraction_view.render_error(str(e), 500)
    
    def get_fractions_by_owner(self, owner_id):
        """
        Handle get fractions by owner request.
        
        Args:
            owner_id: Owner user ID
            
        Returns:
            Response: JSON response with fractions list
        """
        try:
            fractions = self.fraction_service.get_fractions_by_owner(owner_id)
            return self.fraction_view.render_fractions_list(fractions)
        except Exception as e:
            return self.fraction_view.render_error(str(e), 500)
    
    def get_fractions_by_asset(self, asset_id):
        """
        Handle get fractions by asset request.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Response: JSON response with fractions list
        """
        try:
            fractions = self.fraction_service.get_fractions_by_asset(asset_id)
            return self.fraction_view.render_fractions_list(fractions)
        except Exception as e:
            return self.fraction_view.render_error(str(e), 500)
    
    def update_fraction(self, fraction_id):
        """
        Handle fraction update request.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            Response: JSON response with updated fraction data
        """
        try:
            fraction_data = request.get_json()
            if not fraction_data:
                return self.fraction_view.render_error("No JSON data provided", 400)
            
            fraction = self.fraction_service.update_fraction(fraction_id, fraction_data)
            if not fraction:
                return self.fraction_view.render_error("Fraction not found", 404)
            
            return self.fraction_view.render_fraction_updated(fraction)
        except Exception as e:
            return self.fraction_view.render_error(str(e), 500)
    
    def delete_fraction(self, fraction_id):
        """
        Handle fraction deletion request.
        
        Args:
            fraction_id: Fraction ID
            
        Returns:
            Response: JSON response with deletion status
        """
        try:
            success = self.fraction_service.delete_fraction(fraction_id)
            if not success:
                return self.fraction_view.render_error("Fraction not found", 404)
            
            return self.fraction_view.render_fraction_deleted()
        except Exception as e:
            return self.fraction_view.render_error(str(e), 500)
    
    def get_active_fractions(self):
        """
        Handle get active fractions request.
        
        Returns:
            Response: JSON response with active fractions list
        """
        try:
            fractions = self.fraction_service.get_active_fractions()
            return self.fraction_view.render_fractions_list(fractions)
        except Exception as e:
            return self.fraction_view.render_error(str(e), 500)