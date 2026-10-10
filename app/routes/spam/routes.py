from app.controllers import SpamController
from . import bp


@bp.route('/', methods=['GET'])
def index():
    return SpamController().index()


@bp.route('/predict', methods=['POST'])
def predict():
    """Receive a text message and return the spam classification."""
    return SpamController().predict()
