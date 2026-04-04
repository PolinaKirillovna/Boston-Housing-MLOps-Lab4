"""Training pipeline for the Boston Housing regression model."""

from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from src.config import BASE_DIR, load_config


CONFIG = load_config()

DATA_PATH = BASE_DIR / CONFIG["paths"]["train_data"]
MODEL_PATH = BASE_DIR / CONFIG["paths"]["model_path"]

RANDOM_STATE = CONFIG.getint("project", "random_state")
TARGET_COL = CONFIG["project"]["target_col"]
ID_COL = CONFIG["project"]["id_col"]

TEST_SIZE = CONFIG.getfloat("training", "test_size")

FEATURE_COLUMNS = [
    "crim",
    "zn",
    "indus",
    "chas",
    "nox",
    "rm",
    "age",
    "dis",
    "rad",
    "tax",
    "ptratio",
    "black",
    "lstat",
]


def rmse_score(y_true: pd.Series, y_pred: np.ndarray) -> float:
    """Calculate Root Mean Squared Error.

    Args:
        y_true: Ground truth target values.
        y_pred: Predicted target values.

    Returns:
        RMSE value as float.
    """
    mse = mean_squared_error(y_true, y_pred)
    return float(np.sqrt(mse))


def load_training_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    """Load training dataset from CSV.

    Args:
        data_path: Path to the training CSV file.

    Returns:
        Loaded pandas DataFrame.

    Raises:
        FileNotFoundError: If training file does not exist.
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Training file not found: {data_path}")

    return pd.read_csv(data_path)


def build_features_and_target(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Split input dataframe into features and target.

    Args:
        df: Raw training dataframe.

    Returns:
        Tuple of feature matrix X and target vector y.

    Raises:
        ValueError: If required columns are missing.
    """
    required_columns = set(FEATURE_COLUMNS + [TARGET_COL, ID_COL])
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns in train dataset: {sorted(missing)}")

    x_data = df[FEATURE_COLUMNS].copy()
    y_data = df[TARGET_COL].copy()
    return x_data, y_data


def create_model() -> RandomForestRegressor:
    """Create RandomForestRegressor from configuration.

    Returns:
        Configured RandomForestRegressor instance.
    """
    max_depth_raw = CONFIG["model"].get("max_depth", "").strip()
    max_depth = int(max_depth_raw) if max_depth_raw else None

    return RandomForestRegressor(
        n_estimators=CONFIG.getint("model", "n_estimators"),
        max_depth=max_depth,
        min_samples_split=CONFIG.getint("model", "min_samples_split"),
        min_samples_leaf=CONFIG.getint("model", "min_samples_leaf"),
        random_state=RANDOM_STATE,
        n_jobs=CONFIG.getint("model", "n_jobs"),
    )


def save_model(model: RandomForestRegressor, model_path: Path = MODEL_PATH) -> None:
    """Persist trained model to disk.

    Args:
        model: Trained model instance.
        model_path: Destination path for serialized model.
    """
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


def train_model() -> Tuple[RandomForestRegressor, float]:
    """Train model, evaluate it, and save artifact to disk.

    Returns:
        Tuple containing trained model and validation RMSE.
    """
    df = load_training_data()
    x_data, y_data = build_features_and_target(df)

    x_train, x_valid, y_train, y_valid = train_test_split(
        x_data,
        y_data,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    model = create_model()
    model.fit(x_train, y_train)

    predictions = model.predict(x_valid)
    rmse = rmse_score(y_valid, predictions)

    save_model(model)

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Validation RMSE: {rmse:.4f}")

    return model, rmse


if __name__ == "__main__":
    train_model()