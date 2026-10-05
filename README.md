# flask-app-ml

Academic Flask application that serves pre-trained machine learning models over
a web interface and a REST API. This repository currently implements **image
classification inference** with a pre-trained CIFAR-10 Keras model.

## Features

- Web page to upload an image and see the predicted category and confidence.
- Canonical REST API: `POST /api/predict` and `GET /api/models`.
- Confidence messaging: predictions below 50% confidence are flagged as uncertain.
- Lazy, thread-safe model loading (the model is loaded once and reused).

## Requirements

- Python 3.11+ (developed and tested on Python 3.14).
- The ML backend: **Keras 3 with the PyTorch backend**. TensorFlow is not used
  because it publishes no wheels for Python 3.14; Keras is the framework named in
  the project constitution and the backend is a runtime detail.

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
   FLASK_CONFIG=development
   APP_NAME=flask-app-ml
   KERAS_BACKEND=torch
   SQLALCHEMY_DEVELOPMENT_DATABASE_URI=sqlite:///flask-app-ml_dev.db
   ```

3. Ensure the model artifact is present at `app/models/weights/cifar10.keras`
   and registered in `app/models/registry.json` (see `app/models/weights/cifar10.md`).

## Run

```powershell
python run.py
```

- Web UI: `http://127.0.0.1:5000/images`
- API: `http://127.0.0.1:5000/api/predict` and `http://127.0.0.1:5000/api/models`

## API

### `POST /api/predict` (canonical)

Multipart form field `image` (JPG/PNG/WEBP, max 5 MB).

```json
{
  "message": "Detecté: gato (87.0% de certeza).",
  "prediction": "gato",
  "confidence": 87.0,
  "uncertain": false,
  "model": "cifar10"
}
```

### `GET /api/models`

Returns the available models with metadata (internal artifact paths omitted).

### `POST /images/analyze` (UI entry point)

Same capability as `/api/predict`, used by the web page; returns the same JSON.

Errors return `{"error": "..."}` with status `400` (missing/invalid image),
`413` (too large), or `500` (inference failure), and never expose internal
details.

## Tests

```powershell
pytest -q
```

## Project structure

```text
app/
├── ml/                # registry, preprocessing, predictor, inference service
├── models/            # ORM models + registry.json + weights/
├── controllers/       # image_controller, api_controller
├── routes/            # images blueprint, api blueprint
└── templates/
config/
tests/                 # unit + integration tests
```
