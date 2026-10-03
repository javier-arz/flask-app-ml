"""Tests for the images blueprint."""

import io
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('development')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestImagesIndex:
    """Tests for GET /images/"""

    def test_index_returns_200(self, client):
        """GET /images/ should return HTTP 200."""
        response = client.get('/images/')
        assert response.status_code == 200

    def test_index_contains_form(self, client):
        """GET /images/ should contain the upload form."""
        response = client.get('/images/')
        html = response.data.decode('utf-8')
        assert 'uploadForm' in html
        assert 'enctype="multipart/form-data"' in html

    def test_index_contains_file_input(self, client):
        """GET /images/ should contain file input with image accept."""
        response = client.get('/images/')
        html = response.data.decode('utf-8')
        assert 'type="file"' in html
        assert 'accept="image/*"' in html
        assert 'name="image"' in html


class TestImagesAnalyze:
    """Tests for POST /images/analyze"""

    def test_analyze_without_file_returns_400(self, client):
        """POST /images/analyze without file should return HTTP 400."""
        response = client.post('/images/analyze')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No image file provided'

    def test_analyze_with_file_returns_200(self, client):
        """POST /images/analyze with file should return HTTP 200."""
        data = {
            'image': (io.BytesIO(b'test image content'), 'test.jpg')
        }
        response = client.post(
            '/images/analyze',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        result = response.get_json()
        assert 'message' in result
        assert result['message'] == 'Imagen Recibida'

    def test_analyze_with_png_file_returns_200(self, client):
        """POST /images/analyze with PNG file should return HTTP 200."""
        data = {
            'image': (io.BytesIO(b'test png content'), 'test.png')
        }
        response = client.post(
            '/images/analyze',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        result = response.get_json()
        assert result['message'] == 'Imagen Recibida'

    def test_analyze_response_is_json(self, client):
        """POST /images/analyze should return JSON content type."""
        data = {
            'image': (io.BytesIO(b'test image content'), 'test.jpg')
        }
        response = client.post(
            '/images/analyze',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.content_type == 'application/json'


class TestNavigation:
    """Tests for navigation."""

    def test_main_page_has_navigation(self, client):
        """Main page should contain navigation."""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '<nav' in html
        assert 'Análisis de Imágenes' in html

    def test_images_page_has_navigation(self, client):
        """Images page should contain navigation."""
        response = client.get('/images/')
        html = response.data.decode('utf-8')
        assert '<nav' in html
        assert 'Análisis de Imágenes' in html
