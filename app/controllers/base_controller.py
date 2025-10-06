"""
Base controller class with common functionality.
"""

from abc import ABC


class BaseController(ABC):
    """Base controller class with common exception handling."""
    
    def handle_request(self, operation, *args, **kwargs):
        """
        Handle a request with common exception handling.
        
        Args:
            operation: Function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Response from the operation or error response
        """
        try:
            return operation(*args, **kwargs)
        except ValueError as e:
            return self.view.render_error(str(e), 400)  # pylint: disable=no-member
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)  # pylint: disable=no-member
    
    def handle_simple_request(self, operation):
        """
        Handle a simple request with common exception handling.
        
        Args:
            operation: Function to execute (no arguments)
            
        Returns:
            Response from the operation or error response
        """
        try:
            return operation()
        except ValueError as e:
            return self.view.render_error(str(e), 400)  # pylint: disable=no-member
        except Exception as e:
            return self.view.render_error(f"Server error: {str(e)}", 500)  # pylint: disable=no-member
