import os
from datetime import timedelta
from dotenv import load_dotenv

# Import Environment variables

load_dotenv()  # reads variables from a .env file and sets them in os.environ

class BaseConfig():
    FLASK_CONFIG = os.environ.get('FLASK_CONFIG')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    APP_NAME = os.environ.get('APP_NAME')

    # Image analysis / ML inference
    # Maximum accepted upload size (bytes). Bounds memory usage.
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))
    # Confidence (percentage) below which a prediction is flagged as uncertain.
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', 50))
    # Optional override for the model registry manifest location.
    MODEL_REGISTRY_PATH = os.environ.get('MODEL_REGISTRY_PATH')
