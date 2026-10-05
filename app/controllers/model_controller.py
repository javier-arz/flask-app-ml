"""Controller for the model catalog (``GET /api/models``)."""

from __future__ import annotations

from flask import jsonify

from app.ml.inference_service import list_models


class ModelController:
    """Handles ``GET /api/models`` (model listing)."""

    def models(self):
        """List the available models with their public metadata."""
        return jsonify({"models": list_models()}), 200
