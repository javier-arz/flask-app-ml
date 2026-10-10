# flask-app-ml

Academic Flask application that serves pre-trained machine learning models over
a web interface and a REST API. This repository currently implements **image
classification inference** with a pre-trained CIFAR-10 Keras model.

## Features

- Web page to upload an image and see the predicted category and confidence.
- Web page to input text and detect if it is spam.
- Loading spinner shown while the content is being analyzed.
- Image prediction endpoint: `POST /images/predict`.
- Spam detection endpoint: `POST /spam/predict`.
- Model catalog endpoint: `GET /api/models`.
- Confidence messaging: predictions below 50% confidence are flagged as uncertain.
- Lazy, thread-safe model loading (the model is loaded once and reused).

## Requirements

- Python 3.11+ (developed and tested on Python 3.14).
- The ML backend for image inference: **Keras 3 with the PyTorch backend**.
- The ML backend for spam detection: **Keras 3 with TensorFlow** (required by the
  `TextVectorization` layer in the spam model).

## Setup

1. Create and activate a virtual environment, then install dependencies:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Configure environment variables (copy `.env.example` to `.env`):

   ```text
   SECRET_KEY=...
   FLASK_APP=run.py
   FLASK_CONFIG=development
   APP_NAME=flask-app-ml
   KERAS_BACKEND=torch
   SQLALCHEMY_DEVELOPMENT_DATABASE_URI=sqlite:///flask-app-ml_dev.db
   ```

3. Ensure the model artifact is present at `app/models/weights/cifar10.keras`
   and registered in `app/models/registry.json` (see `app/models/weights/cifar10.md`).

## Run

```powershell
flask run
```

- Image analysis UI: `http://127.0.0.1:5000/images`
- Spam detection UI: `http://127.0.0.1:5000/spam`
- Model catalog: `http://127.0.0.1:5000/api/models`

> **Note**: `python run.py` only creates the app and configures logging; it does
> not start the server. Use `flask run` (with `FLASK_APP=run.py`).

## API

### `POST /images/predict`

Multipart form field `image` (JPG/PNG/WEBP, max 5 MB). This is the single
prediction endpoint (used by the web page).

Confident result (confidence ≥ 50%):

```json
{
  "message": "Detecté: gato (87.0% de certeza).",
  "prediction": "gato",
  "confidence": 87.0,
  "uncertain": false,
  "model": "cifar10"
}
```

Uncertain result (confidence < 50%):

```json
{
  "message": "Detecté: gato (32.4% de certeza). No estoy completamente seguro de esta predicción.",
  "prediction": "gato",
  "confidence": 32.4,
  "uncertain": true,
  "model": "cifar10"
}
```

### `POST /spam/predict`

Form field `text` (plain text, max 10,000 characters). Returns the spam
classification with confidence.

```json
{
  "message": "Detecté: spam (95.3% de certeza).",
  "prediction": "spam",
  "confidence": 95.3,
  "uncertain": false,
  "model": "spam_classifier"
}
```

### `GET /api/models`

Returns the available models with metadata (internal artifact paths omitted).

Errors return `{"error": "..."}` with status `400` (missing/invalid input),
`413` (too large), or `500` (inference failure), and never expose internal
details.

## Tests

```powershell
pytest -q
```

## Project structure

```text
app/
├── ml/                # model registry, preprocessing, predictor, inference service
├── models/            # ORM models + registry.json + weights/
├── controllers/       # main_controller, image_controller, model_controller, spam_controller
├── routes/            # mains, images, spam, api blueprints
├── templates/         # base.html, mains/index.html, images/index.html, spam/index.html
└── static/            # compiled Tailwind CSS
config/                # environment configuration
tests/                 # unit + integration tests
```
