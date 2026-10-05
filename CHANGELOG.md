# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Image ML inference with a pre-trained CIFAR-10 model:
  - Single prediction endpoint `POST /images/predict` returning a real prediction
  - `GET /api/models` endpoint listing available models with metadata
  - Confidence messaging: results below 50% confidence are flagged as uncertain
  - Loading spinner shown while the image is being analyzed
  - JSON error handling (400/413/500) without leaking internal details
  - Model registry, preprocessing and predictor modules; unit and integration tests (`pytest`)
  - README, model card, quickstart, OpenAPI contracts and constitution update (v1.1.0)
- Image analysis view with upload form and AJAX endpoint
  - `POST /images/analyze` endpoint with stub response
  - Navigation menu shared across all pages via `base.html` block
  - Automated tests for images blueprint (`tests/test_images.py`)
  - Tailwind CSS v4.3.3 compiled locally
  - Spec Kit documentation for image-analysis feature
  - CHANGELOG.md and GitHub PR template

### Changed

- Consolidated the duplicate prediction endpoints into a single `POST /images/predict`
- Renamed `ApiController` to `ModelController`

### Removed

- Stub endpoints `POST /images/analyze` and `POST /api/predict`
- Unused macOS-only `run.sh` helper
