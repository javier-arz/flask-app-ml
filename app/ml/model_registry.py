"""Loads and validates the model metadata manifest (``app/models/registry.json``).

Follows the project constitution sections 4.1 (storage convention) and 4.2
(model metadata). The registry is the single source of truth for model
metadata, and the accessor here exposes a sanitized "public view" for the
``GET /api/models`` endpoint (no internal artifact paths).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ``app/ml/model_registry.py`` -> parents[2] is the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = (PROJECT_ROOT / "app" / "models").resolve()
DEFAULT_REGISTRY_PATH = MODELS_DIR / "registry.json"

ALLOWED_TYPES = {"regression", "classification", "clustering"}
ALLOWED_MODALITIES = {"image", "text"}


class ModelRegistryError(Exception):
    """Raised when the registry manifest is missing or invalid."""


@dataclass(frozen=True)
class ModelMetadata:
    """Typed view of a single model entry from the registry manifest."""

    name: str
    type: str
    input_modality: str
    input_shape: list[int]
    output_shape: list[int]
    classes: list[dict[str, str]]
    framework: str = "keras"
    artifact_path: str = ""
    confidence_threshold: float = 50.0

    def public_view(self) -> dict[str, Any]:
        """Return the metadata safe for external exposure (no file paths)."""
        return {
            "name": self.name,
            "type": self.type,
            "input_modality": self.input_modality,
            "input_shape": self.input_shape,
            "output_shape": self.output_shape,
            "classes": self.classes,
            "framework": self.framework,
            "confidence_threshold": self.confidence_threshold,
        }


def _require(raw: dict[str, Any], key: str, model_name: str) -> Any:
    if key not in raw:
        raise ModelRegistryError(
            f"Model '{model_name}' is missing required field '{key}'"
        )
    return raw[key]


def _build_metadata(raw: dict[str, Any], base_dir: Path) -> ModelMetadata:
    name = str(_require(raw, "name", "<unknown>"))

    model_type = str(_require(raw, "type", name))
    if model_type not in ALLOWED_TYPES:
        raise ModelRegistryError(
            f"Model '{name}' has invalid type '{model_type}'; "
            f"expected one of {sorted(ALLOWED_TYPES)}"
        )

    modality = str(_require(raw, "input_modality", name))
    if modality not in ALLOWED_MODALITIES:
        raise ModelRegistryError(
            f"Model '{name}' has invalid input_modality '{modality}'; "
            f"expected one of {sorted(ALLOWED_MODALITIES)}"
        )

    input_shape = list(_require(raw, "input_shape", name))
    output_shape = list(_require(raw, "output_shape", name))
    classes = list(_require(raw, "classes", name))

    if not output_shape:
        raise ModelRegistryError(f"Model '{name}' has an empty output_shape")
    if len(classes) != int(output_shape[0]):
        raise ModelRegistryError(
            f"Model '{name}': len(classes)={len(classes)} does not match "
            f"output_shape[0]={output_shape[0]}"
        )

    for entry in classes:
        if not isinstance(entry, dict) or "key" not in entry or "label" not in entry:
            raise ModelRegistryError(
                f"Model '{name}': each class must be an object with "
                "'key' and 'label'"
            )

    threshold = float(_require(raw, "confidence_threshold", name))
    if not 0 <= threshold <= 100:
        raise ModelRegistryError(
            f"Model '{name}': confidence_threshold must be between 0 and 100"
        )

    artifact_rel = str(_require(raw, "artifact_path", name))
    artifact_path = (base_dir / artifact_rel).resolve()
    if artifact_path != MODELS_DIR and MODELS_DIR not in artifact_path.parents:
        raise ModelRegistryError(
            f"Model '{name}': artifact_path '{artifact_rel}' escapes app/models"
        )
    if not artifact_path.is_file():
        raise ModelRegistryError(
            f"Model '{name}': artifact not found at '{artifact_path}'"
        )

    return ModelMetadata(
        name=name,
        type=model_type,
        input_modality=modality,
        input_shape=input_shape,
        output_shape=output_shape,
        classes=classes,
        framework=str(raw.get("framework", "keras")),
        artifact_path=str(artifact_path),
        confidence_threshold=threshold,
    )


def load_registry(path: str | Path | None = None) -> list[ModelMetadata]:
    """Load and validate every model entry in the registry manifest.

    Raises:
        ModelRegistryError: if the manifest is missing, malformed, or any
            entry violates the validation rules.
    """
    registry_path = Path(path) if path is not None else DEFAULT_REGISTRY_PATH
    if not registry_path.is_file():
        raise ModelRegistryError(f"Registry manifest not found at '{registry_path}'")

    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelRegistryError(
            f"Registry manifest '{registry_path}' could not be parsed: {exc}"
        ) from exc

    models = data.get("models") if isinstance(data, dict) else None
    if not isinstance(models, list) or not models:
        raise ModelRegistryError(
            "Registry manifest must contain a non-empty 'models' list"
        )

    base_dir = registry_path.parent
    return [_build_metadata(raw, base_dir) for raw in models]


def get_model(name: str | None = None) -> ModelMetadata:
    """Return a model by name, or the first model when ``name`` is omitted."""
    models = load_registry()
    if name is None:
        return models[0]
    for model in models:
        if model.name == name:
            return model
    raise ModelRegistryError(f"Model '{name}' is not registered")
