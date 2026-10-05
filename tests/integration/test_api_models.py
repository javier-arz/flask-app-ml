"""Integration tests for the model listing endpoint: GET /api/models."""


def test_models_lists_cifar10(client):
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.get_json()
    assert "models" in data
    names = [model["name"] for model in data["models"]]
    assert "cifar10" in names
    assert all("artifact_path" not in model for model in data["models"])
