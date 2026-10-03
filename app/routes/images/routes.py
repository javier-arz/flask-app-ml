from app.controllers import ImageController
from . import bp


@bp.route('/', methods=['GET'])
def index():
    return ImageController().index()


@bp.route('/analyze', methods=['POST'])
def analyze():
    """Receive an uploaded image and return a confirmation response.
    
    TODO: Replace stub response with actual ML model inference
    in a future feature.
    """
    return ImageController().analyze()
