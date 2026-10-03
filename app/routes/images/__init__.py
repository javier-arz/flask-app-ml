from flask import Blueprint

bp = Blueprint('images', __name__)

from app.routes.images import routes
