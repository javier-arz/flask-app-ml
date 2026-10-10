"""Integration tests for the spam prediction endpoint."""

from __future__ import annotations

import pytest


class TestSpamPredictEndpoint:
    """Integration tests for POST /spam/predict."""

    def test_predict_page_loads(self, client):
        """The spam prediction page should load successfully."""
        response = client.get('/spam/')
        assert response.status_code == 200
        assert 'Detección de Spam'.encode('utf-8') in response.data

    def test_predict_spam_text(self, client):
        """POST /spam/predict should classify spam text."""
        response = client.post('/spam/predict', data={
            'text': '¡Gana dinero gratis! Click aquí para tu premio'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['prediction'] == 'spam'
        assert data['confidence'] > 80.0
        assert data['uncertain'] is False
        assert data['model'] == 'spam_classifier'
        assert 'spam' in data['message'].lower()

    def test_predict_ham_text(self, client):
        """POST /spam/predict should classify legitimate text."""
        response = client.post('/spam/predict', data={
            'text': 'Hola, te escribo para coordinar la reunión de mañana'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['prediction'] == 'no spam'
        assert data['confidence'] > 60.0
        assert data['uncertain'] is False
        assert data['model'] == 'spam_classifier'

    def test_predict_empty_text(self, client):
        """POST /spam/predict should reject empty text."""
        response = client.post('/spam/predict', data={'text': ''})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'No se recibió ningún texto' in data['error']

    def test_predict_whitespace_only_text(self, client):
        """POST /spam/predict should reject whitespace-only text."""
        response = client.post('/spam/predict', data={'text': '   \n\t  '})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_predict_no_text_field(self, client):
        """POST /spam/predict should reject missing text field."""
        response = client.post('/spam/predict', data={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_predict_text_too_long(self, client):
        """POST /spam/predict should reject text exceeding max length."""
        long_text = 'a' * 10001
        response = client.post('/spam/predict', data={'text': long_text})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'longitud máxima' in data['error']


class TestModelListing:
    """Tests for GET /api/models including spam classifier."""

    def test_spam_model_in_listing(self, client):
        """The spam classifier should appear in the model listing."""
        response = client.get('/api/models')
        assert response.status_code == 200
        data = response.get_json()
        model_names = [m['name'] for m in data['models']]
        assert 'spam_classifier' in model_names

    def test_spam_model_metadata(self, client):
        """The spam classifier should have correct metadata."""
        response = client.get('/api/models')
        data = response.get_json()
        spam_model = next(m for m in data['models'] if m['name'] == 'spam_classifier')
        assert spam_model['type'] == 'classification'
        assert spam_model['input_modality'] == 'text'
        assert spam_model['output_shape'] == [2]
        assert len(spam_model['classes']) == 2
        assert spam_model['framework'] == 'keras'
        assert spam_model['confidence_threshold'] == 50.0
