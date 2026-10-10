from flask import Blueprint

bp = Blueprint('spam', __name__)

from app.routes.spam import routes
