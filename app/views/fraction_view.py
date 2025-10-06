"""
Fraction view for formatting fraction-related responses.
"""

from flask import jsonify
from .base_view import BaseView


class FractionView(BaseView):
    """View class for fraction responses."""
    
    def __init__(self):
        """Initialize FractionView with entity name."""
        super().__init__('Fraction')
    
    def render_fraction(self, fraction):
        """
        Render single fraction response.
        
        Args:
            fraction: Fraction model instance
            
        Returns:
            Response: JSON response
        """
        return self.render_single(fraction)
    
    def render_fraction_created(self, fraction):
        """
        Render fraction creation response.
        
        Args:
            fraction: Created Fraction model instance
            
        Returns:
            Response: JSON response
        """
        return self.render_created(fraction)
    
    def render_fraction_updated(self, fraction):
        """
        Render fraction update response.
        
        Args:
            fraction: Updated Fraction model instance
            
        Returns:
            Response: JSON response
        """
        return self.render_updated(fraction)
    
    def render_fraction_deleted(self):
        """
        Render fraction deletion response.
        
        Returns:
            Response: JSON response
        """
        return self.render_deleted()
    
    def render_fractions_list(self, fractions):
        """
        Render fractions list response.
        
        Args:
            fractions: List of Fraction model instances
            
        Returns:
            Response: JSON response
        """
        return self.render_list(fractions, 'fractions')