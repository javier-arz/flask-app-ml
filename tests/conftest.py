"""Pytest fixtures shared across the test suite."""

import pytest

from app import create_app


@pytest.fixture
def app():
    """Create a Flask application configured for testing."""
    application = create_app('development')
    application.config['TESTING'] = True
    return application


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()
