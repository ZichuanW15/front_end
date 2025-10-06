"""
Fraction view for formatting fraction-related responses.
"""

from flask import jsonify


class FractionView:
    """View class for fraction responses."""
    
    def render_fraction(self, fraction):
        """
        Render single fraction response.
        
        Args:
            fraction: Fraction model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'fraction': fraction.to_dict(),
            'status': 'success'
        })
    
    def render_fraction_created(self, fraction):
        """
        Render fraction creation response.
        
        Args:
            fraction: Created Fraction model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'fraction': fraction.to_dict(),
            'message': 'Fraction created successfully',
            'status': 'success'
        }), 201
    
    def render_fraction_updated(self, fraction):
        """
        Render fraction update response.
        
        Args:
            fraction: Updated Fraction model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'fraction': fraction.to_dict(),
            'message': 'Fraction updated successfully',
            'status': 'success'
        })
    
    def render_fraction_deleted(self):
        """
        Render fraction deletion response.
        
        Returns:
            Response: JSON response
        """
        return jsonify({
            'message': 'Fraction deleted successfully',
            'status': 'success'
        })
    
    def render_fractions_list(self, fractions):
        """
        Render fractions list response.
        
        Args:
            fractions: List of Fraction model instances
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            'fractions': [fraction.to_dict() for fraction in fractions],
            'count': len(fractions),
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
            'error': 'Fraction Error',
            'message': error_message,
            'status_code': status_code
        }), status_code