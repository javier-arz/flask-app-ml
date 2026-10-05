"""Tests for the images blueprint."""

import pytest
from app import create_app
from app.ml import inference_service
from tests.helpers import image_upload


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

    def test_index_contains_loading_indicator(self, client):
        """GET /images/ should contain the progress indicator and spinner."""
        response = client.get('/images/')
        html = response.data.decode('utf-8')
        assert 'id="loading"' in html
        assert 'class="spinner"' in html
        assert "fetch('/images/predict'" in html


class TestImagesPredict:
    """Tests for POST /images/predict (real ML inference)."""

    def test_predict_without_file_returns_400(self, client):
        """POST /images/predict without file should return HTTP 400."""
        response = client.post('/images/predict')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == inference_service.NO_IMAGE_MESSAGE

    def test_predict_with_file_returns_200(self, client, monkeypatch):
        """POST /images/predict with a valid image should return HTTP 200."""
        monkeypatch.setattr(inference_service.predictor, 'predict', lambda a: (3, 87.0))
        response = client.post(
            '/images/predict',
            data=image_upload(filename='test.jpg'),
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        result = response.get_json()
        assert result['prediction'] == 'gato'
        assert 'message' in result

    def test_predict_with_png_file_returns_200(self, client, monkeypatch):
        """POST /images/predict with PNG file should return HTTP 200."""
        monkeypatch.setattr(inference_service.predictor, 'predict', lambda a: (3, 87.0))
        response = client.post(
            '/images/predict',
            data=image_upload(filename='test.png'),
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        result = response.get_json()
        assert result['prediction'] == 'gato'

    def test_predict_response_is_json(self, client, monkeypatch):
        """POST /images/predict should return JSON content type."""
        monkeypatch.setattr(inference_service.predictor, 'predict', lambda a: (0, 90.0))
        response = client.post(
            '/images/predict',
            data=image_upload(filename='test.jpg'),
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
