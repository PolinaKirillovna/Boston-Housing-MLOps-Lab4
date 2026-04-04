"""Shared pytest fixtures for project tests."""

from pathlib import Path

import joblib
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor

from src.train import FEATURE_COLUMNS


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create sample dataframe for training and prediction tests."""
    rows = []
    for idx in range(20):
        rows.append(
            {
                "ID": idx + 1,
                "crim": 0.01 + idx * 0.001,
                "zn": float(idx),
                "indus": 7.0 + idx * 0.1,
                "chas": idx % 2,
                "nox": 0.4 + idx * 0.001,
                "rm": 6.0 + idx * 0.05,
                "age": 50.0 + idx,
                "dis": 4.0 + idx * 0.1,
                "rad": 1 + (idx % 5),
                "tax": 200 + idx,
                "ptratio": 15.0 + idx * 0.1,
                "black": 390.0 - idx,
                "lstat": 5.0 + idx * 0.1,
                "medv": 20.0 + idx * 0.5,
            }
        )
    return pd.DataFrame(rows)


@pytest.fixture
def trained_model(sample_dataframe: pd.DataFrame) -> RandomForestRegressor:
    """Train a lightweight model for testing."""
    x_data = sample_dataframe[FEATURE_COLUMNS]
    y_data = sample_dataframe["medv"]

    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(x_data, y_data)
    return model


@pytest.fixture
def saved_model(tmp_path: Path, trained_model: RandomForestRegressor) -> Path:
    """Persist a temporary trained model and return its path."""
    model_path = tmp_path / "model.joblib"
    joblib.dump(trained_model, model_path)
    return model_path