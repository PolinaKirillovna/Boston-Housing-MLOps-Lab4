"""Tests for training pipeline."""

from pathlib import Path

import pandas as pd
import pytest

from src import train


def test_rmse_score_returns_float() -> None:
    """RMSE helper should return zero for identical predictions."""
    actual = pd.Series([1.0, 2.0, 3.0])
    predicted = [1.0, 2.0, 3.0]

    result = train.rmse_score(actual, predicted)

    assert isinstance(result, float)
    assert result == 0.0


def test_build_features_and_target_success(sample_dataframe: pd.DataFrame) -> None:
    """Feature and target split should return expected columns."""
    x_data, y_data = train.build_features_and_target(sample_dataframe)

    assert list(x_data.columns) == train.FEATURE_COLUMNS
    assert len(y_data) == len(sample_dataframe)


def test_build_features_and_target_raises_on_missing_columns(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Function should fail if required columns are missing."""
    broken_df = sample_dataframe.drop(columns=["rm"])

    with pytest.raises(ValueError, match="Missing required columns"):
        train.build_features_and_target(broken_df)


def test_load_training_data_reads_csv(tmp_path: Path, sample_dataframe: pd.DataFrame) -> None:
    """Training data loader should read existing CSV files."""
    csv_path = tmp_path / "train.csv"
    sample_dataframe.to_csv(csv_path, index=False)

    loaded_df = train.load_training_data(csv_path)

    assert not loaded_df.empty
    assert list(loaded_df.columns) == list(sample_dataframe.columns)


def test_load_training_data_raises_if_file_missing(tmp_path: Path) -> None:
    """Training data loader should raise for missing file."""
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        train.load_training_data(missing_path)