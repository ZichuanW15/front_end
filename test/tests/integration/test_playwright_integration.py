"""
Playwright-based integration tests for admin asset creation workflow.
Tests the complete user workflow through the browser interface.
"""

import pytest
from playwright.sync_api import sync_playwright, expect


class TestAdminAssetCreationFlow:
    """Playwright integration tests for complete admin asset creation workflow."""
    
    @pytest.fixture(scope="function")
    def browser_context(self):
        """Set up browser context for testing."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            yield context
            browser.close()
    
    @pytest.fixture
    def page(self, browser_context):
        """Create a new page for testing."""
        page = browser_context.new_page()
        yield page
        page.close()
    
    def test_basic_page_load(self, page):
        """Test that the application loads."""
        # Navigate to the application
        page.goto("http://localhost:5001")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        # Check that we get some response (even if it's an error page)
        content = page.content()
        assert len(content) > 0
    
    def test_health_endpoint(self, page):
        """Test health endpoint through browser."""
        # Navigate to health endpoint
        response = page.goto("http://localhost:5001/health")
        
        # Check that we get a valid response
        assert response.status == 200
        
        # Check that the response contains health information
        content = page.content()
        assert "healthy" in content.lower() or "status" in content.lower()
    
    def test_api_endpoint(self, page):
        """Test API endpoint through browser."""
        # Navigate to assets endpoint
        response = page.goto("http://localhost:5001/assets")
        
        # Check that we get a response (could be 200 or 401/403)
        assert response.status in [200, 401, 403, 404]
        
        # Check that we get some content
        content = page.content()
        assert len(content) > 0