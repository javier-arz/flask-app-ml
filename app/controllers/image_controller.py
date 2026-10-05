"""Controller for the images blueprint (the single prediction entry point)."""

from __future__ import annotations

from flask import jsonify, render_template, request

from app.ml.inference_service import InferenceError, analyze_file


class ImageController:
    def index(self) -> str:
        return render_template('images/index.html')

    def predict(self):
        """Analyze an uploaded image and return the prediction as JSON.

        Preserves the message-based response consumed by the page.
        """
        try:
            result = analyze_file(request.files.get('image'))
        except InferenceError as error:
            return jsonify({'error': error.message}), error.status_code
        return jsonify(result.to_dict()), 200
