"""Tests for batch prediction module."""

from pathlib import Path

import pandas as pd
import pytest

from src import predict
from src.train import FEATURE_COLUMNS


def test_validate_feature_columns_success(sample_dataframe: pd.DataFrame) -> None:
    """Validation should pass when all features are present."""
    df = sample_dataframe[FEATURE_COLUMNS].copy()
    predict.validate_feature_columns(df)


def test_validate_feature_columns_raises(sample_dataframe: pd.DataFrame) -> None:
    """Validation should fail when any feature is missing."""
    df = sample_dataframe.drop(columns=["rm"])

    with pytest.raises(ValueError, match="Missing feature columns"):
        predict.validate_feature_columns(df)


def test_load_model_raises_for_missing_model(tmp_path: Path) -> None:
    """Model loader should fail for absent model file."""
    missing_model_path = tmp_path / "missing_model.joblib"

    with pytest.raises(FileNotFoundError):
        predict.load_model(missing_model_path)


def test_predict_from_dataframe_returns_predictions(
    monkeypatch,
    sample_dataframe: pd.DataFrame,
    trained_model,
) -> None:
    """Prediction function should return one prediction per input row."""
    df = sample_dataframe[FEATURE_COLUMNS].copy()

    monkeypatch.setattr(predict, "load_model", lambda: trained_model)

    predictions = predict.predict_from_dataframe(df)

    assert len(predictions) == len(df)


def test_predict_test_file_creates_submission(
    monkeypatch,
    tmp_path: Path,
    sample_dataframe: pd.DataFrame,
    trained_model,
) -> None:
    """Batch prediction should create submission dataframe."""
    test_df = sample_dataframe.drop(columns=["medv"]).copy()
    test_csv_path = tmp_path / "test.csv"
    test_df.to_csv(test_csv_path, index=False)

    monkeypatch.setattr(predict, "load_model", lambda: trained_model)
    monkeypatch.setattr(predict, "SUBMISSION_PATH", tmp_path / "submission.csv")

    submission = predict.predict_test_file(test_csv_path)

    assert list(submission.columns) == ["ID", "medv"]
    assert len(submission) == len(test_df)
    assert (tmp_path / "submission.csv").exists()