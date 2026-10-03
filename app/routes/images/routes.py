from app.controllers import ImageController
from . import bp

@bp.route('/', methods=['GET'])
def index():
    return ImageController().index()
