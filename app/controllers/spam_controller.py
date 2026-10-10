"""Controller for the spam blueprint (text spam detection)."""

from __future__ import annotations

from flask import jsonify, render_template, request

from app.ml.inference_service import InferenceError, analyze_text


class SpamController:
    def index(self) -> str:
        return render_template('spam/index.html')

    def predict(self):
        """Analyze a text message and return the spam classification as JSON.

        Preserves the message-based response consumed by the page.
        """
        try:
            result = analyze_text(request.form.get('text'))
        except InferenceError as error:
            return jsonify({'error': error.message}), error.status_code
        return jsonify(result.to_dict()), 200
