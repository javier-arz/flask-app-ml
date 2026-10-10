# Spam Classifier Model Card

## Model Overview

| Property | Value |
|----------|-------|
| Name | spam_classifier |
| Type | Binary classification |
| Input modality | Text (Spanish) |
| Output | Probability of spam (0-1) |
| Framework | Keras 3 + TensorFlow |
| Artifact | `weights/mi_modelo_spam.keras` |
| Total params | 241,253 (942.40 KB) |

## Architecture

| # | Layer | Type | Output Shape | Params |
|---|-------|------|--------------|--------|
| 0 | text_vectorization | TextVectorization | (None, 100) | 0 |
| 1 | embedding | Embedding | (None, 100, 16) | 80,000 |
| 2 | global_average_pooling1d | GlobalAveragePooling1D | (None, 16) | 0 |
| 3 | dense | Dense | (None, 16) | 272 |
| 4 | dropout | Dropout | (None, 16) | 0 |
| 5 | dense_1 | Dense | (None, 8) | 136 |
| 6 | dense_2 | Dense | (None, 1) | 9 |

## Preprocessing

The model includes an integrated `TextVectorization` layer that handles all
text preprocessing internally:

| Parameter | Value |
|-----------|-------|
| max_tokens | 5000 |
| standardize | lower_and_strip_punctuation |
| split | whitespace |
| ngrams | None |
| output_mode | int |
| output_sequence_length | 100 |
| vocabulary_size | 3138 |

## Classes

| Index | Key | Label |
|-------|-----|-------|
| 0 | ham | no spam |
| 1 | spam | spam |

## Usage

```python
from app.ml.spam_predictor import predict

class_index, confidence = predict("¡Gana dinero gratis!")
# class_index: 1 (spam), confidence: 95.3
```

## Limitations

- The model was trained on Spanish text; performance on other languages may vary.
- The vocabulary is limited to 3,138 words; out-of-vocabulary words are mapped to `[UNK]`.
- The model does not handle images or other non-text inputs.
- Maximum input length is 10,000 characters (enforced at the service level).

## Provenance

- Trained externally (Google Colab / Jupyter Notebook).
- Exported as `.keras` artifact.
- Integrated into flask-app-ml for academic purposes.
