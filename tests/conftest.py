import os
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Важно: env должны быть заданы до импортов app.main / db.session
os.environ.setdefault("MSSQL_SERVER", "dummy")
os.environ.setdefault("MSSQL_PORT", "1433")
os.environ.setdefault("MSSQL_DATABASE", "dummy")
os.environ.setdefault("MSSQL_USER", "dummy")
os.environ.setdefault("MSSQL_PASSWORD", "dummy")
os.environ.setdefault("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_123456789")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("MODEL_VERSION", "test-model")

from app.dependencies.database import get_db
from app.main import app
from db.base import Base
from db.models import PredictionLog, User  # noqa: F401


@pytest.fixture()
def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID": 1,
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
                "medv": 28.5,
            },
            {
                "ID": 2,
                "crim": 0.03237,
                "zn": 0.0,
                "indus": 2.18,
                "chas": 0,
                "nox": 0.458,
                "rm": 6.998,
                "age": 45.8,
                "dis": 6.0622,
                "rad": 3,
                "tax": 222,
                "ptratio": 18.7,
                "black": 394.63,
                "lstat": 2.94,
                "medv": 33.4,
            },
        ]
    )


@pytest.fixture()
def trained_model(sample_dataframe: pd.DataFrame):
    features = sample_dataframe.drop(columns=["ID", "medv"])
    target = sample_dataframe["medv"]

    model = RandomForestRegressor(
        n_estimators=10,
        random_state=42,
    )
    model.fit(features, target)
    return model


@pytest.fixture()
def db_session(tmp_path: Path):
    db_file = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
