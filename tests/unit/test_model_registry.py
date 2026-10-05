"""Unit tests for the model registry manifest validation."""

import json

import pytest

from app.ml import model_registry
from app.ml.model_registry import ModelRegistryError, load_registry

# Absolute path to a real, existing artifact under app/models.
_VALID_ARTIFACT = str(model_registry.MODELS_DIR / "weights" / "cifar10.keras")


def _entry(**overrides) -> dict:
    entry = {
        "name": "test",
        "type": "classification",
        "input_modality": "image",
        "input_shape": [32, 32, 3],
        "output_shape": [2],
        "classes": [{"key": "a", "label": "A"}, {"key": "b", "label": "B"}],
        "preprocessing": {},
        "framework": "keras",
        "artifact_path": _VALID_ARTIFACT,
        "confidence_threshold": 50,
    }
    entry.update(overrides)
    return entry


def _write(tmp_path, entry: dict):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"models": [entry]}), encoding="utf-8")
    return path


def test_valid_registry_loads(tmp_path):
    models = load_registry(_write(tmp_path, _entry()))
    assert models[0].name == "test"
    assert models[0].artifact_path.endswith("cifar10.keras")


def test_classes_length_mismatch_raises(tmp_path):
    path = _write(tmp_path, _entry(output_shape=[10]))
    with pytest.raises(ModelRegistryError):
        load_registry(path)


def test_invalid_type_raises(tmp_path):
    path = _write(tmp_path, _entry(type="banana"))
    with pytest.raises(ModelRegistryError):
        load_registry(path)


def test_invalid_modality_raises(tmp_path):
    path = _write(tmp_path, _entry(input_modality="audio"))
    with pytest.raises(ModelRegistryError):
        load_registry(path)


def test_invalid_threshold_raises(tmp_path):
    path = _write(tmp_path, _entry(confidence_threshold=150))
    with pytest.raises(ModelRegistryError):
        load_registry(path)


def test_path_traversal_raises(tmp_path):
    path = _write(tmp_path, _entry(artifact_path="../../etc/passwd"))
    with pytest.raises(ModelRegistryError):
        load_registry(path)


def test_missing_artifact_raises(tmp_path):
    path = _write(
        tmp_path,
        _entry(artifact_path=str(model_registry.MODELS_DIR / "weights" / "nope.keras")),
    )
    with pytest.raises(ModelRegistryError):
        load_registry(path)


def test_missing_manifest_raises(tmp_path):
    with pytest.raises(ModelRegistryError):
        load_registry(tmp_path / "does-not-exist.json")


def test_public_view_hides_artifact_path():
    model = load_registry()[0]
    assert "artifact_path" not in model.public_view()
