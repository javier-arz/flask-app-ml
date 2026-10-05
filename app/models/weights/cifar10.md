# Model Card: CIFAR-10 Image Classifier (`cifar10`)

## Overview

- **Name**: `cifar10`
- **Type**: Classification (multi-class, single-label)
- **Input modality**: Image
- **Framework**: Keras 3 (artifact saved with `keras_version: 3.13.2`)
- **Artifact**: `app/models/weights/cifar10.keras`
- **Registry entry**: `app/models/registry.json`

## Architecture

- `Sequential` model.
- Input tensor: `(None, 32, 32, 3)`, `float32`, RGB.
- Layers: `InputLayer` → data augmentation (`RandomFlip`, `RandomRotation`, `RandomZoom`, `RandomTranslation`) → 3× (`Conv2D` → `BatchNormalization` → `MaxPooling2D`) → `Flatten` → `Dense(256, relu)` → `Dropout` → `Dense(128, relu)` → `Dropout` → `Dense(10, softmax)`.
- The augmentation layers are inactive at inference time.
- No built-in rescaling layer: normalization is applied during preprocessing (see below).

## Preprocessing (must match training)

Documented in `app/models/registry.json` and implemented in `app/ml/preprocessing.py`:

1. Decode bytes to an image (OpenCV), convert **BGR → RGB**.
2. Resize to **32×32** (`INTER_AREA`).
3. Cast to `float32` and scale by **1/255** → `[0, 1]`.
4. Add a batch dimension → `(1, 32, 32, 3)`.

> **Known limitation**: the exact training-time normalization is not recorded in the artifact. The `1/255` scheme is the common CIFAR-10 convention; if predictions are poor on known samples, switch the single `SCALE` constant in `preprocessing.py` (e.g., to CIFAR-10 channel-wise mean/std standardization). See `research.md` R3.

## Categories

Output index → label (canonical key → Spanish display label):

| Index | Key | Label |
|-------|-----|-------|
| 0 | airplane | avión |
| 1 | automobile | automóvil |
| 2 | bird | ave |
| 3 | cat | gato |
| 4 | deer | ciervo |
| 5 | dog | perro |
| 6 | frog | rana |
| 7 | horse | caballo |
| 8 | ship | barco |
| 9 | truck | camión |

## Provenance

- Provided by the project author as part of the Machine Learning Avanzado specialization.
- Source exports: `best_cifar10.keras` and `cifar10_model (1).h5`.
- Training data: CIFAR-10 (60,000 32×32 color images across 10 classes).

## Intended use

- Academic demonstration of an end-to-end inference pipeline (preprocessing → prediction → JSON response).
- Not intended for production, safety-critical, or high-stakes decisions.

## Limitations & ethics

- Low-resolution input (32×32) yields coarse predictions; unrelated images may still receive a class with low confidence.
- No PII is processed; uploaded images are not persisted.
- Predictions are restricted to the ten training categories; the model cannot detect out-of-distribution content except through low confidence.
- Results below the 50% confidence threshold are flagged as uncertain in the API/UI response.
