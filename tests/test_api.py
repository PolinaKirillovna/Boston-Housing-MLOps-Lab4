def test_health_endpoint(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "model_exists" in data


def test_feature_metadata_endpoint(client) -> None:
    response = client.get("/feature-metadata")
    assert response.status_code == 200

    data = response.json()
    assert "features" in data
    assert "target" in data
    assert data["target"] == "medv"
    assert len(data["features"]) == 13
