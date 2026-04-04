from app.auth.security import create_access_token


class DummyModel:
    def predict(self, df):
        return [33.9643]


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_exists" in data


def test_db_health(client):
    response = client.get("/db-health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "reachable",
    }


def test_register_user(client):
    response = client.post(
        "/register",
        json={
            "username": "polina",
            "password": "strongpass123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "polina"
    assert "id" in data


def test_register_duplicate_user(client):
    client.post(
        "/register",
        json={
            "username": "polina",
            "password": "strongpass123",
        },
    )

    response = client.post(
        "/register",
        json={
            "username": "polina",
            "password": "strongpass123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_login_user(client):
    client.post(
        "/register",
        json={
            "username": "polina",
            "password": "strongpass123",
        },
    )

    response = client.post(
        "/login",
        json={
            "username": "polina",
            "password": "strongpass123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/register",
        json={
            "username": "polina",
            "password": "strongpass123",
        },
    )

    response = client.post(
        "/login",
        json={
            "username": "polina",
            "password": "wrongpass",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_predict_requires_auth(client):
    response = client.post(
        "/predict",
        json={
            "crim": 0.02729,
            "zn": 0.0,
            "indus": 7.07,
            "chas": 0,
            "nox": 0.469,
            "rm": 7.185,
            "age": 61.1,
            "dis": 4.9671,
            "rad": 2,
            "tax": 242,
            "ptratio": 17.8,
            "black": 392.83,
            "lstat": 4.03,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_predict_with_auth(client, monkeypatch):
    from app import main as main_module

    def fake_load_model():
        return DummyModel()

    monkeypatch.setattr(main_module, "load_model", fake_load_model)

    register_response = client.post(
        "/register",
        json={
            "username": "polina",
            "password": "strongpass123",
        },
    )
    user_id = register_response.json()["id"]

    token = create_access_token(subject="polina")

    response = client.post(
        "/predict",
        json={
            "crim": 0.02729,
            "zn": 0.0,
            "indus": 7.07,
            "chas": 0,
            "nox": 0.469,
            "rm": 7.185,
            "age": 61.1,
            "dis": 4.9671,
            "rad": 2,
            "tax": 242,
            "ptratio": 17.8,
            "black": 392.83,
            "lstat": 4.03,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["stored"] is True
    assert "request_id" in data
    assert data["predicted_medv"] == 33.9643

    # дополнительно проверим, что user реально участвует в логике
    assert user_id == 1
