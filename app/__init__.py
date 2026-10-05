import time

from config import config
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Logging a user's authentication state handler
login_manager = LoginManager()

# ORM Database handler
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name) -> Flask:
    """Creates a Flask application Instance."""
    app = Flask(__name__)

    # apply configuration
    app.config.from_object(config[config_name])

    # Expose global values to every Jinja template.
    @app.context_processor
    def inject_globals():
        return {
            "time": time,
        }

    # initialize extensions: order matters
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.routes.mains import bp as mains_blueprint
    app.register_blueprint(mains_blueprint)

    from app.routes.images import bp as images_blueprint
    app.register_blueprint(images_blueprint, url_prefix='/images')

    from app.routes.api import bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Return a JSON error for oversized uploads instead of HTML."""
        return jsonify({
            'error': 'La imagen excede el tamaño máximo permitido (5 MB).'
        }), 413

    return app
