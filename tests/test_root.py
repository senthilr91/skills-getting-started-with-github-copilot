"""Tests for the root endpoint."""

import pytest


class TestRootEndpoint:
    """Test cases for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that the root endpoint redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_with_follow_redirects(self, client):
        """Test that following the redirect returns a successful response."""
        response = client.get("/", follow_redirects=True)
        
        # The actual HTML content will be returned
        assert response.status_code == 200
