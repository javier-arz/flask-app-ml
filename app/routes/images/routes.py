from app.controllers import ImageController
from . import bp


@bp.route('/', methods=['GET'])
def index():
    return ImageController().index()


@bp.route('/predict', methods=['POST'])
def predict():
    """Receive an uploaded image and return the model's prediction."""
    return ImageController().predict()
