"""
Base view class for common response formatting patterns.
"""

from flask import jsonify


class BaseView:
    """Base view class with common response methods."""
    
    def __init__(self, entity_name):
        """
        Initialize base view with entity name.
        
        Args:
            entity_name: Name of the entity (e.g., 'Asset', 'Fraction')
        """
        self.entity_name = entity_name
    
    def render_single(self, entity):
        """
        Render single entity response.
        
        Args:
            entity: Model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            self.entity_name.lower(): entity.to_dict(),
            'status': 'success'
        })
    
    def render_created(self, entity):
        """
        Render entity creation response.
        
        Args:
            entity: Created model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            self.entity_name.lower(): entity.to_dict(),
            'message': f'{self.entity_name} created successfully',
            'status': 'success'
        }), 201
    
    def render_updated(self, entity):
        """
        Render entity update response.
        
        Args:
            entity: Updated model instance
            
        Returns:
            Response: JSON response
        """
        return jsonify({
            self.entity_name.lower(): entity.to_dict(),
            'message': f'{self.entity_name} updated successfully',
            'status': 'success'
        })
    
    def render_deleted(self):
        """
        Render entity deletion response.
        
        Returns:
            Response: JSON response
        """
        return jsonify({
            'message': f'{self.entity_name} deleted successfully',
            'status': 'success'
        })
    
    def render_list(self, entities, entity_key=None):
        """
        Render entities list response.
        
        Args:
            entities: List of model instances
            entity_key: Key name for the list (defaults to entity_name + 's')
            
        Returns:
            Response: JSON response
        """
        if entity_key is None:
            entity_key = f"{self.entity_name.lower()}s"
        
        return jsonify({
            entity_key: [entity.to_dict() for entity in entities],
            'count': len(entities),
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
            'error': f'{self.entity_name} Error',
            'message': error_message,
            'status_code': status_code
        }), status_code