"""Routes for the REST API blueprint."""

from app.controllers import ModelController
from . import bp


@bp.route('/models', methods=['GET'])
def models():
    """List the available models with their metadata."""
    return ModelController().models()
