"""Prediction utilities for batch inference on Boston Housing data."""

from pathlib import Path

import joblib
import pandas as pd

from src.config import BASE_DIR, load_config
from src.train import FEATURE_COLUMNS


CONFIG = load_config()

TEST_DATA_PATH = BASE_DIR / CONFIG["paths"]["test_data"]
MODEL_PATH = BASE_DIR / CONFIG["paths"]["model_path"]
SUBMISSION_PATH = BASE_DIR / CONFIG["paths"]["submission_path"]

ID_COL = CONFIG["project"]["id_col"]


def load_model(model_path: Path = MODEL_PATH):
    """Load serialized model artifact from disk.

    Args:
        model_path: Path to the saved model.

    Returns:
        Deserialized model instance.

    Raises:
        FileNotFoundError: If model file does not exist.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}. Run training first."
        )

    return joblib.load(model_path)


def validate_feature_columns(df: pd.DataFrame) -> None:
    """Validate that all required feature columns are present.

    Args:
        df: Input dataframe for inference.

    Raises:
        ValueError: If any expected features are missing.
    """
    missing = set(FEATURE_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing feature columns: {sorted(missing)}")


def predict_from_dataframe(df: pd.DataFrame):
    """Generate predictions for a dataframe.

    Args:
        df: Input dataframe containing model features.

    Returns:
        Array-like model predictions.
    """
    validate_feature_columns(df)

    model = load_model()
    x_data = df[FEATURE_COLUMNS]
    predictions = model.predict(x_data)
    return predictions


def predict_test_file(test_path: Path = TEST_DATA_PATH) -> pd.DataFrame:
    """Run batch prediction for test.csv and create submission.csv.

    Args:
        test_path: Path to test CSV file.

    Returns:
        Submission dataframe with columns ID and medv.

    Raises:
        FileNotFoundError: If test file does not exist.
        ValueError: If ID column is missing.
    """
    if not test_path.exists():
        raise FileNotFoundError(f"Test file not found: {test_path}")

    test_df = pd.read_csv(test_path)

    if ID_COL not in test_df.columns:
        raise ValueError(f"Missing ID column: {ID_COL}")

    predictions = predict_from_dataframe(test_df)

    submission = pd.DataFrame(
        {
            ID_COL: test_df[ID_COL],
            "medv": predictions,
        }
    )

    submission.to_csv(SUBMISSION_PATH, index=False)

    print(f"Submission file saved to: {SUBMISSION_PATH}")
    print(submission.head())

    return submission


if __name__ == "__main__":
    predict_test_file()